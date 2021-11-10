"""Classes for models with related entities."""

import logging
from typing import TYPE_CHECKING, Optional, Union

from django.apps import apps
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.celery import app
from core.fields.custom_m2m_field import CustomManyToManyField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.model import ExtendedModel
from core.models.relations.moderated import ModeratedPositionedRelation
from core.utils.sync import delay

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class AbstractImageRelation(ModeratedPositionedRelation):
    """
    Abstract base model for image relations.

    Models governing m2m relationships between `Image` and another model
    should inherit from this abstract model.
    """

    image = ManyToManyForeignKey(
        to='images.Image',
        related_name='%(app_label)s_%(class)s_set',
    )

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self.image}'

    def content_object(self) -> models.ForeignKey:
        """Foreign key to the model that references the image."""
        raise NotImplementedError


class ImagesField(CustomManyToManyField):
    """Custom field for m2m relationship with images."""

    target_model = 'images.Image'
    through_model_base = AbstractImageRelation

    def __init__(self, through: Union[type[AbstractImageRelation], str], **kwargs):
        """Construct the field."""
        kwargs['through'] = through
        kwargs['verbose_name'] = _('images')
        super().__init__(**kwargs)


class ModelWithImages(ExtendedModel):
    """
    A model that has one or more associated images.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    image_relations: 'QuerySet[AbstractImageRelation]'

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    @property
    def image_relations(self) -> 'QuerySet[AbstractImageRelation]':
        """
        Require the intermediate model to specify `related_name='image_relations'`.

        Models inheriting from ModelWithImages must have a m2m relationship
        with the Image model with a `through` model that inherits from
        AbstractImageRelation and uses `related_name='image_relations'`.
        For example:

        ``
        class ImageRelation(AbstractImageRelation):
            content_object = ManyToManyForeignKey(
                to='propositions.Proposition',
                related_name='image_relations',
            )
        ``
        """

    @property
    def images(self) -> ImagesField:
        """
        Require implementation of an `images` field on inheriting models.

        For example:
        ``
        images = ImagesField(through=ImageRelation)
        ``
        """
        raise NotImplementedError

    @property
    def cached_images(self) -> list:
        """Return the model instance's cached images."""
        images = self.cache.get('images', [])
        if images or not self.images.exists():
            return images
        images = [relation.image.serialize() for relation in self.image_relations.all()]
        delay(
            cache_images,
            f'{self.__class__._meta.app_label}.{self.__class__.__name__.lower()}',
            self.pk,
            images,
        )
        return images

    @property
    def primary_image(self) -> Optional[dict]:
        """Return the image to represent the model instance by default."""
        try:
            return self.cached_images[0]
        except IndexError:
            logging.debug(f'No image could be retrieved for {self}')
            return None


@app.task
def cache_images(model: str, instance_id: int, images: list):
    """Save cached images to a model instance."""
    if not images:
        return
    Model = apps.get_model(model)  # noqa: N806
    if not hasattr(Model, 'cache'):
        logging.error(f'{Model} has no cache.')
        return
    model_instance: ModelWithImages = Model.objects.get(pk=instance_id)
    model_instance.cache['images'] = images
    model_instance.save(wipe_cache=False, moderate=False)
