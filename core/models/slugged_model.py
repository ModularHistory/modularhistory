import logging
from typing import Optional

from autoslug import AutoSlugField
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from core.utils.html import soupify

from .model import Model


class SluggedModel(Model):
    """
    A model with a detail page and slug.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    slug = AutoSlugField(
        verbose_name=_('slug'),
        null=True,
        blank=True,
        editable=True,
        unique=True,
        db_index=True,
        populate_from='get_slug',
    )

    class Meta:
        abstract = True

    def get_absolute_url(self) -> str:  # noqa: DJ12
        """Return the URL for the model instance detail page."""
        absolute_url = ''
        slug = getattr(self, 'slug', None)
        try:
            if slug:
                absolute_url = reverse(
                    f'{self.get_meta().app_label}:detail_slug', args=[str(slug)]
                )
            else:
                absolute_url = reverse(
                    f'{self.get_meta().app_label}:detail', args=[str(self.pk)]
                )
            logging.debug(f'Determined absolute URL: {absolute_url}')
            return absolute_url
        except Exception as err:
            logging.error(f'{err}')
        return absolute_url

    @property
    def absolute_url(self) -> str:
        """Return the URL for the model instance detail page."""
        return self.get_absolute_url()

    @property
    def detail_link(self) -> SafeString:
        """Return a link to the model instance's detail page."""
        return self.get_detail_link()

    @property
    def detail_url(self) -> str:
        """Return the URL of the model instance's detail page."""
        return reverse(f'{self.get_meta().app_label}:detail', args=[self.pk])

    def get_detail_link(self, content: Optional[str] = None) -> SafeString:
        """Return a link to the model instance's detail page."""
        content = content or '<i class="fas fa-info-circle"></i>'
        return format_html(f'<a href="{self.detail_url}" target="_blank">{content}</a>')

    def get_slug(self):
        """Get a slug for the model instance."""
        slug = None
        slug_base_field = getattr(self, 'slug_base_field', None)
        if slug_base_field:
            slug_base = str(getattr(self, slug_base_field, self.pk))
            if '<' in slug_base:
                slug_base = soupify(slug_base).get_text()
            slug = slugify(slug_base)
        return slug or self.pk
