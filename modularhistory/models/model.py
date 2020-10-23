"""Base model classes for ModularHistory."""

import re
from typing import Any, ClassVar, List, Optional, Pattern, Tuple, Type

from aenum import Constant
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model as DjangoModel
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from typedmodels.models import TypedModel as BaseTypedModel

from modularhistory.models.manager import Manager

FieldList = List[str]

# TODO: Extend BaseTypedModel when it's possible.
# Currently, only one level of inheritance from BaseTypedModel is permitted, unfortunately.
TypedModel: Type[BaseTypedModel] = BaseTypedModel


class Model(DjangoModel):
    """Model with additional properties used in ModularHistory apps."""

    class FieldNames(Constant):
        pk = 'pk'

    objects: Manager = Manager()
    searchable_fields: ClassVar[Optional[FieldList]] = None

    admin_placeholder_regex: Pattern

    class Meta:
        abstract = True

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
        return reverse(f'{self._meta.app_label}:detail', args=[self.id])

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

    def get_detail_link(self) -> SafeString:
        """Return a link to the model instance's detail page."""
        return format_html(
            f'<a href="{self.detail_url}" target="_blank">'
            f'<i class="fas fa-info-circle"></i></a>'
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

    @classmethod
    def get_object_html(
        cls, match: re.Match, use_preretrieved_html: bool = False
    ) -> str:
        """Return a model instance's HTML based on a placeholder in the admin."""
        if not cls.admin_placeholder_regex.match(match.group(0)):
            raise ValueError(f'{match} does not match {cls.admin_placeholder_regex}')

        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(3)
            if preretrieved_html:
                return preretrieved_html.strip()

        key = match.group(1).strip()
        model_instance = cls.objects.get(pk=key)
        return model_instance.html
