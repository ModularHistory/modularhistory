from typing import TYPE_CHECKING, Type

from django.db.models.manager import Manager

from apps.moderation.models.changeset.queryset import ChangeSetQuerySet

if TYPE_CHECKING:
    from apps.moderation.models.changeset import ChangeSet


class ChangeSetManager(Manager):

    model: Type['ChangeSet']

    def get_queryset(self):
        return ChangeSetQuerySet(self.model, using=self._db)

    # TODO: clean up
    # def get_for_instance(self, instance):
    #     """Returns Moderation for given model instance"""
    #     try:
    #         moderation = self.get(
    #             object_id=instance.pk,
    #             content_type=ContentType.objects.get_for_model(instance.__class__),
    #         )
    #     except self.model.MultipleObjectsReturned:
    #         # Get the most recent one
    #         moderation = self.filter(
    #             object_id=instance.pk,
    #             content_type=ContentType.objects.get_for_model(instance.__class__),
    #         ).order_by('-updated')[0]
    #     return moderation
