"""Classes for models with related entities."""

from typing import Dict, List, Optional, Sequence, TYPE_CHECKING

from modularhistory.models import Model, retrieve_or_compute

if TYPE_CHECKING:
    from django.db.models.manager import Manager, RelatedManager
    from images.models.image import Image
    from django.db.models import ManyToManyField


class ModelWithImages(Model):
    """
    A model that has one or more associated images.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    images: 'ManyToManyField[Sequence[Image], RelatedManager[Image]]'
    image_relations: 'Manager'

    class Meta:
        abstract = True

    @property
    def primary_image(self) -> Optional[Dict]:
        """Return the image to represent the model instance by default."""
        try:
            return self.serialized_images[0]
        except IndexError:
            return None

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='serialized_images')
    def serialized_images(self) -> List[Dict]:
        """Return a list of dictionaries representing the instance's images."""
        return [
            image_relation.image.serialize()
            for image_relation in self.image_relations.all().select_related('image')
        ]
