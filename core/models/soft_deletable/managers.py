from django.db import models

from .queryset import SoftDeletableQueryset


class SoftDeletableManager(models.Manager):
    """
    Manager for models inheriting from SoftDeletableModel.

    Soft-deleted model instances are excluded from querysets.
    """

    _safedelete_visibility_field = 'pk'
    _queryset_class = SoftDeletableQueryset

    def get_queryset(self):
        return self._queryset_class(self.model, using=self._db).filter(deleted__isnull=True)


class SoftDeletableAllManager(SoftDeletableManager):
    """Manager for all objects, regardless of deletion status."""

    def get_queryset(self):
        return self._queryset_class(self.model, using=self._db)


class SoftDeletableDeletedManager(SoftDeletableManager):
    """Manager for deleted objects."""

    def get_queryset(self):
        return self._queryset_class(self.model, using=self._db).filter(deleted__isnull=False)
