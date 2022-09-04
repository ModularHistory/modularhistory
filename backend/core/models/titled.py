from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from titlecase import titlecase

from core.models.model import ExtendedModel


class TitledModel(ExtendedModel):
    """Base model for models of which instances should have a title."""

    title = models.CharField(
        verbose_name=_('title'),
        max_length=120,
        blank=True,
        help_text=('This value can be used as a page header and/or title attribute.'),
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if not self.title:
            try:
                self.title = self.get_default_title()
            except NotImplementedError:
                raise ValidationError('Title must be set.')

    def get_default_title(self) -> str:
        raise NotImplementedError


class TitleCaseField(serializers.CharField):
    def to_representation(self, value: str) -> str:
        return titlecase(super().to_representation(value))
