from typing import TYPE_CHECKING, Type

from django.contrib.contenttypes.models import ContentType
from django.db.models.manager import Manager

from apps.moderation.queryset import ChangeQuerySet

if TYPE_CHECKING:
    from apps.moderation.models.change import Change


class ChangeSetManager(Manager):

    model: Type['Change']

    def get_queryset(self):
        return ChangeQuerySet(self.model, using=self._db)

    def get_for_instance(self, instance):
        """Returns Moderation for given model instance"""
        try:
            moderation = self.get(
                object_id=instance.pk,
                content_type=ContentType.objects.get_for_model(instance.__class__),
            )
        except self.model.MultipleObjectsReturned:
            # Get the most recent one
            moderation = self.filter(
                object_id=instance.pk,
                content_type=ContentType.objects.get_for_model(instance.__class__),
            ).order_by('-updated')[0]
        return moderation
