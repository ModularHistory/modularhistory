"""Base classes for models that appear in ModularHistory search results."""

from typing import Sequence

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.moderation.models.moderated_model import ModeratedModel
from apps.topics.models.taggable_model import TaggableModel


class SearchableModel(TaggableModel, ModeratedModel):
    """
    A model that shows up in ModularHistory's search results; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    title = models.CharField(
        verbose_name=_('title'),
        max_length=120,
        blank=True,
        help_text=(
            'The title can be used for the detail page header and title tag, '
            'SERP result card header, etc. It should be a noun phrase!'
        ),
    )
    hidden = models.BooleanField(
        default=False,
        blank=True,
        help_text='Hide this item from search results.',
    )

    class Meta:
        """Meta options for SearchableModel."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        abstract = True

    slug_base_fields: Sequence[str] = ('title',)

    def clean(self):
        """Prepare the model instance to be saved."""
        if not self.slug:
            self.slug = self.get_slug()
        super().clean()
