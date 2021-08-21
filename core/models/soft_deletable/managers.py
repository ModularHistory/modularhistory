from django.db import models

from .queryset import SoftDeletableQuerySet


class SoftDeletableManager(models.Manager):
    """
    Manager for models inheriting from SoftDeletableModel.

    Soft-deleted model instances are excluded from querysets.
    """

    queryset_cls = SoftDeletableQuerySet

    def get_queryset(self):
        return self.queryset_cls(self.model, using=self._db).filter(deleted__isnull=True)


class SoftDeletableAllManager(SoftDeletableManager):
    """Manager for all objects, regardless of deletion status."""

    def get_queryset(self):
        return self.queryset_cls(self.model, using=self._db)


class SoftDeletableDeletedManager(SoftDeletableManager):
    """Manager for deleted objects."""

    def get_queryset(self):
        return self.queryset_cls(self.model, using=self._db).filter(deleted__isnull=False)
