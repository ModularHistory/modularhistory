"""Based on https://github.com/peopledoc/django-ltree-demo."""

import regex
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import IntegrityError, connection, models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from apps.topologies.fields import LtreeField
from core.models.model import ExtendedModel


class TreeModel(ExtendedModel):
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
    children: 'QuerySet[TreeModel]'  # from parent's `related_name`
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

    id: int

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True
        ordering = ('path',)

    def clean(self):
        super().clean()
        self.key = self.get_key()
        self.validate_parent(raises=ValidationError)
        self.path = self.get_path()

    def pre_save(self):
        super().pre_save()
        self._original_path = self.get_field_value_from_db('path') if self.pk else ''

    def post_save(self):
        super().post_save()
        old_path = self._original_path
        if old_path and self.path != old_path:
            # Update descendants' paths.
            with connection.cursor() as cursor:
                table = f'{self._meta.app_label}_{self._meta.model_name}'
                # https://www.postgresql.org/docs/13/ltree.html
                cursor.execute(
                    f'UPDATE {table} '
                    f"SET path = '{self.path}'::ltree || "
                    f"subpath({table}.path, nlevel('{old_path}'::ltree)) "
                    f"WHERE {table}.path <@ '{old_path}'::ltree AND id != {self.id}"
                )

    @property
    def ancestors(self) -> QuerySet['TreeModel']:
        """Return the model instances's ancestors, based on its LTree field."""
        queryset = self.__class__.objects.filter(path__descendant=self.path)
        return queryset.exclude(id=self.id)

    @property
    def descendants(self) -> QuerySet['TreeModel']:
        """Return the model instances's descendants, based on its LTree field."""
        return self.__class__.objects.exclude(id=self.id).filter(path__ancestor=self.path)

    @property
    def siblings(self) -> QuerySet['TreeModel']:
        """Return the model instances's siblings, based on its LTree field."""
        return self.__class__.objects.exclude(id=self.id).filter(parent_id=self.parent_id)

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

    def validate_parent(self, raises: type[Exception] = ValidationError):
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
