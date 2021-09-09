from factory.django import DjangoModelFactory

from apps.images import models


class ImageFactory(DjangoModelFactory):
    class Meta:
        model = models.Image
