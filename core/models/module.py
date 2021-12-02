"""Base model classes for ModularHistory."""

import logging
from typing import TYPE_CHECKING, Any, ClassVar, Match, Optional, Pattern, Sequence

import regex
from aenum import Constant
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.safestring import SafeString

from apps.moderation.models.searchable import (
    SearchableModeratedManager,
    SearchableModeratedModel,
)
from core.fields.html_field import OBJECT_PLACEHOLDER_REGEX, TYPE_GROUP, PlaceholderGroups
from core.models.model_with_cache import ModelWithCache
from core.models.slugged import SluggedModel
from core.models.typed import TypedModel, TypedModelManager
from core.utils.models import get_html_for_view as get_html_for_view_
from core.utils.string import truncate

if TYPE_CHECKING:
    from django.db.models.manager import Manager

FieldList = list[str]

# TODO: https://docs.djangoproject.com/en/dev/topics/db/optimization/


class Views(Constant):
    """Labels of views for which model instances can generate HTML."""

    DETAIL = 'detail'
    CARD = 'card'


class ModuleManager(SearchableModeratedManager):
    """Manager for modules."""


class Module(SearchableModeratedModel, SluggedModel, ModelWithCache):
    """Base model for models of which instances are presented as modules."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    objects: 'Manager' = ModuleManager()
    searchable_fields: ClassVar[Optional[FieldList]] = None
    placeholder_regex: Optional[str] = None
    slug_base_fields: Sequence[str] = ('title',)

    def clean(self):
        super().clean()
        if not self.slug:
            self.slug = self.get_slug()

    def pre_save(self):
        ModelWithCache.pre_save(self)
        SluggedModel.pre_save(self)
        SearchableModeratedModel.pre_save(self)

    def post_save(self):
        ModelWithCache.post_save(self)
        SluggedModel.post_save(self)
        SearchableModeratedModel.post_save(self)

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
        return regex.compile(pattern)

    @classmethod
    def get_natural_key_fields(cls) -> list:
        """Return the list of fields that comprise a natural key for the model instance."""
        unique_together = getattr(cls.Meta, 'unique_together', None)
        if unique_together:
            unique_together_is_valid = isinstance(unique_together, (list, tuple)) and all(
                isinstance(field_name, str) for field_name in unique_together
            )
            if not unique_together_is_valid:
                raise ValueError(
                    'The `unique_together` value must be an iterable containing strings.'
                )
            return list(unique_together)
        else:
            fields = cls._meta.get_fields()
            unique_fields = []
            for field in fields:
                if getattr(field, 'unique', False):
                    unique_fields.append(field.name)
            if unique_fields:
                return unique_fields
        raise NotImplementedError(
            'Model must have Meta.unique_together and/or `natural_key_fields` method defined.'
        )

    @classmethod
    def get_searchable_fields(cls) -> FieldList:
        """Return a list of fields that can be used to search for instances of the model."""
        return cls.searchable_fields or []

    @property
    def admin_url(self) -> str:
        """Return the model instance's admin URL."""
        return self.get_admin_url()

    @property
    def ctype(self) -> ContentType:
        """Return the model instance's ContentType."""
        return ContentType.objects.get_for_model(self)

    def get_admin_url(self) -> str:
        """Return the URL of the model instance's admin page."""
        model_name = (
            self._meta.model_name
            if not self._meta.proxy
            else self._meta.proxy_for_model.__name__.lower()
        )
        return reverse(
            f'admin:{self._meta.app_label}_{model_name}_change',
            args=[self.pk],
        )

    def get_html_for_view(
        self,
        view: str = Views.DETAIL,
        text_to_highlight: Optional[str] = None,
    ) -> SafeString:
        """Return HTML for the view (e.g., "card" or "detail") of the instance."""
        return get_html_for_view_(
            self, template_name=view, text_to_highlight=text_to_highlight
        )

    def natural_key(self) -> tuple[Any, ...]:
        """Return a tuple of values comprising the model instance's natural key."""
        natural_key_values = []
        for field in self.__class__.get_natural_key_fields():
            if not hasattr(self, field):
                raise AttributeError(f'Model has no `{field}` attribute.')
            natural_key_values.append(getattr(self, field, None))
        return tuple(natural_key_values)

    def preprocess_html(self, html: str) -> str:
        """
        Preprocess the value of an HTML field belonging to the model instance.

        This method can be used to modify the value of an HTML field
        before it is saved.  It is called when HTML fields are cleaned.
        """
        return html

    def serialize(self) -> dict:
        """Return the serialized model instance (dictionary)."""
        return self.get_serializer()(self).data

    @classmethod
    def get_object_html(
        cls,
        match: Match,
        use_preretrieved_html: bool = False,
    ) -> str:
        """Return a model instance's HTML based on a placeholder in the admin."""
        if not cls.get_admin_placeholder_regex().match(match.group(0)):
            raise ValueError(f'{match} does not match {cls.get_admin_placeholder_regex()}')
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(PlaceholderGroups.HTML)
            if preretrieved_html:
                return str(preretrieved_html).strip()
            logging.info(
                f'Could not use preretrieved HTML for '
                f'{match.group(PlaceholderGroups.MODEL_NAME)} '
                f'({match.group(PlaceholderGroups.PK)}); querying db instead.'
            )
        key = match.group(PlaceholderGroups.PK).strip()
        logging.info(f'Retrieving object HTML for {cls.__name__} {key}...')
        try:
            model_instance = cls.objects.get(pk=key)
            object_html = getattr(model_instance, 'html', '')
            logging.debug(f'Retrieved object HTML: {object_html}')
        except ObjectDoesNotExist as e:
            logging.error(f'Unable to retrieve object HTML; {e}')
            return ''
        return object_html

    @classmethod
    def get_updated_placeholder(cls, match: Match) -> str:
        """Return a placeholder for a model instance depicted in an HTML field."""
        if not match:
            logging.error(
                '{cls.__name__}.get_updated_placeholder was called without a match.'
            )
            raise ValueError
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


class TypedModuleManager(TypedModelManager, ModuleManager):
    """Manager for modules inheriting from `TypedModel`."""


class TypedModule(TypedModel, Module):
    """Combination of `TypedModel` and `Module`."""

    typed_model_marker = True

    class Meta:
        abstract = True

    objects = TypedModuleManager()

    def save(self, *args, **kwargs):
        Module.save(self, *args, **kwargs)
