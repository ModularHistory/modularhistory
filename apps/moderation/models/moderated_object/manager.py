from typing import TYPE_CHECKING, Type

from django.contrib.contenttypes.models import ContentType
from django.db.models.manager import Manager

from apps.moderation.queryset import ModeratedObjectQuerySet

if TYPE_CHECKING:
    from apps.moderation.models.moderated_object import ModeratedObject


class MetaClass(type(Manager)):
    def __new__(cls, name, bases, attrs):
        return super(MetaClass, cls).__new__(cls, name, bases, attrs)


class ModeratedObjectManager(Manager):

    model: Type['ModeratedObject']

    def get_queryset(self):
        return ModeratedObjectQuerySet(self.model, using=self._db)

    def get_for_instance(self, instance):
        '''Returns ModeratedObject for given model instance'''
        try:
            moderated_object = self.get(
                object_pk=instance.pk,
                content_type=ContentType.objects.get_for_model(instance.__class__),
            )
        except self.model.MultipleObjectsReturned:
            # Get the most recent one
            moderated_object = self.filter(
                object_pk=instance.pk,
                content_type=ContentType.objects.get_for_model(instance.__class__),
            ).order_by('-updated')[0]
        return moderated_object
