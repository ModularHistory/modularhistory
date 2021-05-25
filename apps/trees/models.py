"""Based on https://github.com/peopledoc/django-ltree-demo."""

from typing import Type

import regex
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import IntegrityError, connection, models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from apps.trees.fields import LtreeField
from core.models.abstract_model import AbstractModelMeta
from core.models.manager import Manager
from core.models.model import Model


class TreeModel(Model, metaclass=AbstractModelMeta):
    """Implements Postgres ltree for self-referencing hierarchy."""

    parent = models.ForeignKey(
        to='self',
        null=True,
        blank=True,
        # Direct children can be accessed via the `children` property.
        related_name='children',
        on_delete=models.CASCADE,
        verbose_name=_('parent'),
    )
    name = models.TextField(verbose_name=_('name'))
    # The `key` field is a unique identifier derived from the `name` field.
    key = models.CharField(
        max_length=32,
        unique=True,
        blank=True,  # Allow to be blank in forms (since it is set automatically).
        validators=[RegexValidator(regex=r'\w*')],
        verbose_name=_('key'),
    )
    # The `path` field represents the path from the root to the node,
    # where each node is represented by its key.
    path = LtreeField()

    class Meta:
        """Meta options for DatedModel."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options
        abstract = True
        ordering = ('path',)

    def save(self, *args, **kwargs):
        """Save the model instance to the database."""
        self.key = self.get_key()
        self.validate_parent(raises=IntegrityError)
        old_path, new_path = self.path, self.get_path()
        path_changed = new_path != old_path and not self._state.adding
        self.path = new_path
        super().save(*args, **kwargs)
        if path_changed:
            # Update descendants' paths.
            with connection.cursor() as cursor:
                table = f'{self._meta.app_label}_{self._meta.model_name}'
                # https://www.postgresql.org/docs/13/ltree.html
                cursor.execute(
                    f'UPDATE {table} '
                    f"SET path = '{new_path}'::ltree || "
                    f"subpath({table}.path, nlevel('{old_path}'::ltree)) "
                    f"WHERE {table}.path <@ '{old_path}'::ltree AND id != {self.id}"
                )

    def clean(self):
        """Prepare the model instance to be saved to the database."""
        self.validate_parent(raises=ValidationError)
        return super().clean()

    @property
    def ancestors(self) -> QuerySet:
        """Return the model instances's ancestors, based on its LTree field."""
        return self.__class__.objects.exclude(pk=self.pk).filter(  # type: ignore
            path__descendant=self.path
        )

    @property
    def descendants(self) -> QuerySet:
        """Return the model instances's descendants, based on its LTree field."""
        return self.__class__.objects.exclude(pk=self.pk).filter(  # type: ignore
            path__ancestor=self.path
        )

    @property
    def siblings(self) -> QuerySet:
        """Return the model instances's siblings, based on its LTree field."""
        return self.__class__.objects.exclude(pk=self.pk).filter(  # type: ignore
            parent_id=self.parent_id
        )

    def get_key(self) -> str:
        """Calculate the model instance's key value based on its name."""
        name: str = self.name
        key = name.lower().replace('&', 'and')
        # Replace spaces and any kind of hyphen/dash with an underscore.
        key = regex.sub(r'(?:\ |\p{Pd})', '_', key)
        # Remove any other non-alphanumeric characters.
        key = regex.sub(r'\W', '', key)
        if self.key != key:
            if self.__class__.objects.filter(key=key).exists():
                raise IntegrityError(
                    f'{self.__class__.__name__} instance with key={key} already exists.'
                )
        return key

    def get_path(self) -> str:
        """Calculate the model instance's path value based on its key and parent."""
        return f'{self.parent.path}.{self.key}' if self.parent else self.key

    def validate_parent(self, raises: Type[Exception] = ValidationError):
        """Validate the model instance's parent."""
        if not self._state.adding:
            if self.parent:
                # Prevent the model instance from being its own parent, which would
                # result in an infinite recursion.
                if self.parent == self:
                    raise raises(f'{self} cannot be its own parent.')
                # Prevent the model instance from having one of its descendants as
                # its parent, which would result in an infinite recursion.
                elif self.descendants.filter(pk=self.parent.pk).exists():
                    raise raises(
                        f'{self} cannot have {self.parent} as its parent; '
                        f'{self.parent} is a descendant of {self}.'
                    )
