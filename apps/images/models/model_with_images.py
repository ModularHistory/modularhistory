"""Classes for models with related entities."""

import logging
from typing import Dict, Optional

from celery import shared_task
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from core.fields.sorted_m2m_field import SortedManyToManyField
from core.models.model import Model


class ModelWithImages(Model):
    """
    A model that has one or more associated images.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    images = SortedManyToManyField(
        to='images.Image',
        related_name='%(class)s_set',
        blank=True,
        verbose_name=_('images'),
    )

    class Meta:
        """Meta options for ModelWithImages."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True

    @property
    def cached_images(self) -> list:
        """Return the model instance's cached images."""
        images = self.cache.get('images', [])
        if images or not self.images.exists():
            return images
        images = [image.serialize() for image in self.images.all()]
        # images = [
        #     image_relation.image.serialize()
        #     for image_relation in self.image_relations.all().select_related('image')
        # ]
        cache_images.delay(
            f'{self.__class__._meta.app_label}.{self.__class__.__name__.lower()}',
            self.id,
            images,
        )
        return images

    @property
    def primary_image(self) -> Optional[Dict]:
        """Return the image to represent the model instance by default."""
        try:
            return self.cached_images[0]
        except IndexError:
            logging.debug(f'No image could be retrieved for {self}')
            return None


@shared_task
def cache_images(model: str, instance_id: int, images: list):
    """Save cached images to a model instance."""
    if not images:
        return
    Model = apps.get_model(model)
    model_instance: ModelWithImages = Model.objects.get(pk=instance_id)  # noqa: N806
    model_instance.cache['images'] = images
    model_instance.save(wipe_cache=False)
