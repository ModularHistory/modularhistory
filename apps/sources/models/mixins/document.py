"""Model classes for documents (as sources)."""

from django.db import models

from apps.sources.models.mixins.page_numbers import PageNumbersMixin

NAME_MAX_LENGTH: int = 100
LOCATION_INFO_MAX_LENGTH: int = 400
DESCRIPTIVE_PHRASE_MAX_LENGTH: int = 100
URL_MAX_LENGTH: int = 200


class DocumentMixin(PageNumbersMixin):
    """A historical document (as a source)."""

    collection = models.ForeignKey(
        to='sources.Collection',
        related_name='%(class)s',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    collection_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='aka acquisition number',
    )
    location_info = models.TextField(
        blank=True,
        help_text=(
            'Ex: John Alexander Papers, Series 1: Correspondence, 1831-1848, Folder 1'
        ),
    )
    descriptive_phrase = models.CharField(
        max_length=DESCRIPTIVE_PHRASE_MAX_LENGTH,
        blank=True,
        help_text='e.g., "on such-and-such letterhead" or "signed by so-and-so"',
    )
    information_url = models.URLField(
        max_length=URL_MAX_LENGTH,
        null=True,
        blank=True,
        help_text='URL for information regarding the document',
    )

    class Meta:
        """Meta options."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
        abstract = True
