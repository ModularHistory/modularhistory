from typing import TYPE_CHECKING, Callable, Union

from django.contrib.admin.utils import NestedObjects
from django.db import models, router
from django.utils import timezone

from core.models.model import ExtendedModel

from .managers import (
    SoftDeletableAllManager,
    SoftDeletableDeletedManager,
    SoftDeletableManager,
)
from .signals import post_softdelete, post_undelete, pre_softdelete
from .utils import related_objects

if TYPE_CHECKING:
    from django.db.models.base import Model

    from apps.moderation.models.moderated_model.model import ModeratedModel


class SoftDeletableModel(ExtendedModel):
    """
    Abstract soft-deletable model.

    Models for which soft deletion should be enabled must inherit from this model.
    """

    deleted = models.DateTimeField(editable=False, null=True)

    # Manager for objects that are not deleted.
    objects = SoftDeletableManager()
    # Manager for all objects, regardless of deletion status.
    all_objects = SoftDeletableAllManager()
    # Manager for deleted objects.
    deleted_objects = SoftDeletableDeletedManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        was_deleted, was_undeleted = False, False
        if self.pk:
            was_previously_deleted = self.__class__.deleted_objects.filter(
                pk=self.pk
            ).exists()
            if was_previously_deleted and not self.deleted:
                was_undeleted = True
            # elif self.deleted and not was_previously_deleted:
            #     was_deleted = True
        super().save(*args, **kwargs)
        if was_undeleted:
            # Send undelete signal.
            using = kwargs.get('using') or router.db_for_write(self.__class__, instance=self)
            post_undelete.send(sender=self.__class__, instance=self, using=using)

    def undelete(self, **kwargs):
        self._undelete(on_save=self.save, **kwargs)

    def _undelete(self, on_save, **kwargs):
        """Undelete a soft-deleted model."""
        assert self.deleted
        self.deleted = None
        on_save(**kwargs)
        for related in related_objects(self):
            if getattr(related, 'deleted', None) is not None:
                related.undelete()

    def delete(self, **kwargs):
        """Override Django's delete behavior."""
        # This avoids a recursive call on `delete`; see
        # https://github.com/makinacorpus/django-safedelete/issues/117.
        self._delete(on_save=self.save, **kwargs)

    def _delete(self, on_save: Callable, **kwargs):
        """Soft-delete behavior."""
        hard: bool = bool(kwargs.pop('hard', self.deleted is not None))
        if hard:
            # Normally hard-delete the object.
            super().delete()
        else:
            # Only soft-delete the object, marking it as deleted.
            # First, soft-delete related objects.
            related_object: Union['ModeratedModel', 'Model']
            for related_object in related_objects(self):
                if not getattr(related_object, 'deleted', None):
                    # patch: child models like article return themselves in related objects
                    is_self = related_object.pk == self.pk
                    if not is_self:
                        related_object.delete(**kwargs)
            self.deleted = timezone.now()
            using = kwargs.get('using') or router.db_for_write(self.__class__, instance=self)
            # send pre_softdelete signal
            pre_softdelete.send(sender=self.__class__, instance=self, using=using)
            on_save(**kwargs)
            # send softdelete signal
            post_softdelete.send(sender=self.__class__, instance=self, using=using)
            collector = NestedObjects(using=router.db_for_write(self))
            collector.collect([self])
            # update fields (SET, SET_DEFAULT or SET_NULL)
            for model, instances_for_fieldvalues in collector.field_updates.items():
                for (field, value), instances in instances_for_fieldvalues.items():
                    query = models.sql.UpdateQuery(model)
                    query.update_batch(
                        [obj.pk for obj in instances],
                        {field.name: value},
                        collector.using,
                    )

    @classmethod
    def has_unique_fields(cls):
        """Checks if one of the fields of this model has a unique constraint set (unique=True).

        It also checks if the model has sets of field names that, taken together, must be unique.

        Args:
            model: Model instance to check
        """
        if cls._meta.unique_together:
            return True

        for field in cls._meta.fields:
            if field._unique:
                return True
        return False

    # We need to overwrite this check to ensure uniqueness is also checked
    # against "deleted" (but still in db) objects.
    # FIXME: Better/cleaner way ?
    def _perform_unique_checks(self, unique_checks):
        errors = {}

        for model_class, unique_check in unique_checks:
            lookup_kwargs = {}
            for field_name in unique_check:
                f = self._meta.get_field(field_name)
                lookup_value = getattr(self, f.attname)
                if lookup_value is None:
                    continue
                if f.primary_key and not self._state.adding:
                    continue
                lookup_kwargs[str(field_name)] = lookup_value
            if len(unique_check) != len(lookup_kwargs):
                continue

            # This is the changed line
            if hasattr(model_class, 'all_objects'):
                qs = model_class.all_objects.filter(**lookup_kwargs)
            else:
                qs = model_class._default_manager.filter(**lookup_kwargs)

            model_class_pk = self._get_pk_val(model_class._meta)
            if not self._state.adding and model_class_pk is not None:
                qs = qs.exclude(pk=model_class_pk)
            if qs.exists():
                if len(unique_check) == 1:
                    key = unique_check[0]
                else:
                    key = models.base.NON_FIELD_ERRORS
                errors.setdefault(key, []).append(
                    self.unique_error_message(model_class, unique_check)
                )
        return errors
