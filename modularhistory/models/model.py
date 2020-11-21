"""Base model classes for ModularHistory."""

import logging
import re
from pprint import pformat
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Match,
    Optional,
    Pattern,
    Tuple,
    Type,
    Union,
)

import serpy
from aenum import Constant
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model as DjangoModel
from django.urls import reverse
from django.utils.html import SafeString, format_html
from rest_framework.serializers import Serializer
from typedmodels.models import TypedModel as BaseTypedModel

from modularhistory.fields.html_field import (
    END_PATTERN,
    OBJECT_PLACEHOLDER_REGEX,
    TYPE_GROUP,
    PlaceholderGroups,
)
from modularhistory.models.manager import Manager
from modularhistory.utils.html import prettify
from modularhistory.utils.models import get_html_for_view as get_html_for_view_
from modularhistory.utils.string import truncate

FieldList = List[str]

# TODO: Extend BaseTypedModel when it's possible.
# Currently, only one level of inheritance from BaseTypedModel is permitted, unfortunately.
TypedModel: Type[BaseTypedModel] = BaseTypedModel

# TODO: https://docs.djangoproject.com/en/3.1/topics/db/optimization/


class Views(Constant):
    """Labels of views for which model instances can generate HTML."""

    DETAIL = 'detail'
    CARD = 'card'


class Model(DjangoModel):
    """Model with additional properties used in ModularHistory apps."""

    class FieldNames(Constant):
        pk = 'pk'

    objects: Manager = Manager()
    searchable_fields: ClassVar[Optional[FieldList]] = None
    serializer: Type[Serializer]
    placeholder_regex: Optional[str] = None

    class Meta:
        """
        Meta options for Model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        abstract = True

    @classmethod
    def get_admin_placeholder_regex(cls) -> Pattern:
        """Return a compiled Regex pattern to match a model instance placeholder."""
        pattern = cls.placeholder_regex
        content_type = cls.__name__.lower()
        if pattern:
            logging.debug(f'Retrieved {content_type} placeholder regex: {pattern}')
        else:
            pattern = OBJECT_PLACEHOLDER_REGEX.replace(
                TYPE_GROUP,
                rf'(?P<{PlaceholderGroups.MODEL_NAME}>{content_type})',
            )
            logging.debug(f'Calculated placeholder regex for {content_type}: {pattern}')
        return re.compile(pattern)

    @classmethod
    def get_searchable_fields(cls) -> FieldList:
        """Return a list of fields that can be used to search for instances of the model."""
        return cls.searchable_fields or []

    @classmethod
    def get_meta(cls):
        """
        Return the model's _meta attribute value.

        This is used purely to avoid warnings about accessing a private attribute.
        """
        return cls._meta

    @property
    def admin_url(self) -> str:
        """Return the model instance's admin URL."""
        return self.get_admin_url()

    @property
    def ctype(self) -> ContentType:
        """Return the model instance's ContentType."""
        return ContentType.objects.get_for_model(self)

    @property
    def detail_link(self) -> SafeString:
        """Return a link to the model instance's detail page."""
        return self.get_detail_link()

    @property
    def detail_url(self) -> str:
        """Return the URL of the model instance's detail page."""
        return reverse(f'{self.get_meta().app_label}:detail', args=[self.id])

    @property
    def natural_key_fields(self) -> Optional[List]:
        """Return the list of fields that comprise a natural key for the model instance."""
        unique_together = getattr(self.Meta, 'unique_together', None)
        if unique_together:
            unique_together_is_valid = isinstance(
                unique_together, (list, tuple)
            ) and all(isinstance(field_name, str) for field_name in unique_together)
            if not unique_together_is_valid:
                raise ValueError(
                    'The `unique_together` value must be an iterable containing strings.'
                )
            return list(unique_together)
        else:
            fields = self._meta.get_fields()
            unique_fields = []
            for field in fields:
                if getattr(field, 'unique', False):
                    unique_fields.append(field.name)
            if unique_fields:
                return unique_fields
        raise NotImplementedError(
            'Model must have Meta.unique_together and/or `natural_key_fields` method defined.'
        )

    def get_admin_url(self):
        """Return the URL of the model instance's admin page."""
        return reverse(
            f'admin:{self._meta.app_label}_{self._meta.model_name}_change',
            args=[self.id],
        )

    def get_detail_link(self, content: Optional[str] = None) -> SafeString:
        """Return a link to the model instance's detail page."""
        content = content or '<i class="fas fa-info-circle"></i>'
        return format_html(f'<a href="{self.detail_url}" target="_blank">{content}</a>')

    def get_html_for_view(
        self,
        view: str = Views.DETAIL,
        text_to_highlight: Optional[str] = None,
    ) -> SafeString:
        """Return HTML for the view (e.g., "card" or "detail") of the instance."""
        return get_html_for_view_(
            self, template_name=view, text_to_highlight=text_to_highlight
        )

    def natural_key(self) -> Tuple[Any, ...]:
        """Return a tuple of values comprising the model instance's natural key."""
        natural_key_values = []
        for field in self.natural_key_fields:
            value = getattr(self, field, None)
            if not value:
                raise AttributeError(f'Model has no `{field}` attribute.')
            natural_key_values.append(value)
        return tuple(natural_key_values)

    def preprocess_html(self, html: str):
        """
        Preprocess the value of an HTML field belonging to the model instance.

        This method can be used to modify the value of an HTML field
        before it is saved.  It is called when HTML fields are cleaned.
        """
        return html

    def serialize(self) -> Dict:
        """Return the serialized model instance (dictionary)."""
        serialized_instance = self.serializer(self).data
        logging.debug(
            f'Serialized {self.__class__.__name__.lower()}:\n'
            f'{pformat(serialized_instance)}'
        )
        return serialized_instance

    @classmethod
    def get_object_html(
        cls,
        match: re.Match,
        use_preretrieved_html: bool = False,
    ) -> str:
        """Return a model instance's HTML based on a placeholder in the admin."""
        if not cls.get_admin_placeholder_regex().match(match.group(0)):
            raise ValueError(f'{match} does not match {cls.admin_placeholder_regex}')

        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(PlaceholderGroups.HTML)
            if preretrieved_html:
                return preretrieved_html.strip()
            logging.info(
                f'Could not use preretrieved HTML for '
                f'{match.group(PlaceholderGroups.MODEL_NAME)} '
                f'({match.group(PlaceholderGroups.PK)}); querying db instead.'
            )
        key = match.group(PlaceholderGroups.PK).strip()
        logging.info(f'Retrieving object HTML for {cls.__name__} {key}...')
        try:
            model_instance = cls.objects.get(pk=key)
            object_html = model_instance.html
            logging.info(f'Retrieved object HTML: {object_html}')
        except ObjectDoesNotExist as e:
            logging.error(f'Unable to retrieve object HTML; {e}')
            return ''
        return object_html

    @classmethod
    def get_object_from_placeholder(
        cls, match: Match, serialize: bool = False
    ) -> Union['Model', Dict]:
        """Given a regex match of a model instance placeholder, return the instance."""
        if not cls.get_admin_placeholder_regex().match(match.group(0)):
            raise ValueError(f'{match} does not match {cls.admin_placeholder_regex}')
        key = match.group(PlaceholderGroups.PK).strip()
        logging.debug(f'Retrieving {cls.__name__} {key}...')
        model_instance: 'Model' = cls.objects.get(pk=key)
        logging.debug(f'Retrieved {cls.__name__} {key}')
        if serialize:
            return model_instance.serialize()
        return model_instance

    @classmethod
    def get_updated_placeholder(cls, match: Match) -> str:
        """Return a placeholder for a model instance depicted in an HTML field."""
        placeholder = match.group(0)
        logging.debug(f'Looking at {truncate(placeholder)}')
        extant_html = match.group(PlaceholderGroups.HTML)
        html = cls.get_object_html(match)
        if extant_html:
            logging.debug(
                f'Replacing extant HTML in {truncate(placeholder)}\n'
                f'{truncate(extant_html)} ---> {truncate(html)}'
            )
            placeholder = placeholder.replace(extant_html, html)
        else:
            model_name = match.group(PlaceholderGroups.MODEL_NAME)
            pk = match.group(PlaceholderGroups.PK)
            placeholder = f'[[ {model_name}: {pk}: {html} ]]'
        logging.debug(f'Updated {placeholder}')
        return placeholder


class ModelSerializer(serpy.Serializer):
    """Base serializer for ModularHistory's models."""

    pk = serpy.Field()
    model = serpy.MethodField()

    def get_model(self, instance: Model) -> str:  # noqa
        """Return the model name of the instance."""
        model_cls: Type[Model] = instance.__class__
        return f'{model_cls.get_meta().app_label}.{model_cls.__name__.lower()}'
