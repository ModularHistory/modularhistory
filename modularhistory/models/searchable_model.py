"""Base classes for models that appear in ModularHistory search results."""

import re
import uuid
from typing import Match, Optional, TYPE_CHECKING

import inflect
from aenum import Constant
from django.db.models import BooleanField, UUIDField
from django.template import loader
from django.utils.html import SafeString, format_html

from modularhistory.models.taggable_model import TaggableModel
from modularhistory.models.model_with_computations import ModelWithComputations
from search.templatetags.highlight import highlight

if TYPE_CHECKING:
    from modularhistory.models.manager import SearchableModelManager

# group 1: model class name
# group 2: model instance pk
# group 3: ignore
# group 4: model instance HTML
# group 5: closing brackets
ADMIN_PLACEHOLDER_REGEX = (
    r'<<\ ?([a-zA-Z]+?):\ ?([\w\d-]+?)(:\ ?(?!>>)([\s\S]+?))?(\ ?>>)'
)
MODEL_NAME_GROUP = 1
PK_GROUP = 2


class Views(Constant):
    """Labels of views for which model instances can generate HTML."""

    DETAIL = 'detail'
    CARD = 'card'


class SearchableModel(TaggableModel, ModelWithComputations):
    """
    A model that shows up in ModularHistory's search results; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    verified = BooleanField(default=False, blank=True)
    hidden = BooleanField(
        default=False,
        blank=True,
        help_text="Don't let this item appear in search results.",
    )
    key = UUIDField(primary_key=False, default=uuid.uuid4, editable=False, unique=True)

    class FieldNames(TaggableModel.FieldNames):
        verified = 'verified'
        hidden = 'hidden'

    class Meta:
        abstract = True

    objects: 'SearchableModelManager'
    admin_placeholder_regex = re.compile(ADMIN_PLACEHOLDER_REGEX)

    def generate_html_for_view(
        self,
        view: str = Views.DETAIL,
    ) -> str:
        """Generate HTML for the model instance's detail page."""
        model_name = f'{self.__class__.__name__}'.lower()
        app_name = inflect.engine().plural(model_name)
        template_directory_name = app_name
        template_name = f'{template_directory_name}/_{view}.html'
        template = loader.get_template(template_name)
        context = {
            model_name: self,
            'object': self,
            'show_edit_links': False,
        }
        return template.render(context)

    def get_html_for_view(
        self,
        view: str = Views.DETAIL,
        text_to_highlight: Optional[str] = None,
    ) -> SafeString:
        """Return HTML for the view (e.g., "card" or "detail") of the instance."""
        # model_name = f'{self.__class__.__name__}'.lower()
        # app_name = inflect.engine().plural(model_name)
        # artifacts_are_used = False
        # if artifacts_are_used:
        #     artifact_subdir = inflect.engine().plural(view)
        #     artifact_name = f'{artifact_subdir}/{self.key}.html'
        #     artifact_path = os.path.join(
        #         settings.BASE_DIR, app_name, 'artifacts', artifact_name
        #     )
        #     if os.path.exists(artifact_path):
        #         logging.info(f'Reading artifact: {artifact_name}')
        #         with open(artifact_path) as artifact:
        #             response = artifact.read()
        response = self.generate_html_for_view(view=view)
        if text_to_highlight:
            response = highlight(response, text_to_highlight=text_to_highlight)
        return format_html(response)

    @classmethod
    def get_updated_placeholder(cls, match: Match) -> str:
        """Return a placeholder for a model instance depicted in an HTML field."""
        placeholder = match.group(0)
        appendage = match.group(3)
        updated_appendage = f': {cls.get_object_html(match)}'
        if appendage:
            updated_placeholder = placeholder.replace(appendage, updated_appendage)
        else:
            updated_placeholder = (
                f'{placeholder.replace(" >>", "").replace(">>", "")}'
                f'{updated_appendage} >>'
            )
        return updated_placeholder.replace('\n\n\n', '\n').replace('\n\n', '\n')

    @classmethod
    def get_object_from_placeholder(cls, match: Match) -> 'SearchableModel':
        """Given a regex match of a model instance placeholder, return the instance."""
        if not cls.admin_placeholder_regex.match(match.group(0)):
            raise ValueError(f'{match} does not match {cls.admin_placeholder_regex}')
        key = match.group(PK_GROUP).strip()
        return cls.objects.get(pk=key)
