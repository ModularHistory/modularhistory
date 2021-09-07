from typing import Optional

from autoslug import AutoSlugField
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from apps.redirects.models import Redirect
from core.models.titled import TitledModel
from core.utils.html import soupify


class SluggedModel(TitledModel):
    """Base model for models of which instances have a detail page and slug."""

    slug = AutoSlugField(
        verbose_name=_('slug'),
        blank=True,
        editable=True,
        unique=True,
        db_index=True,
        populate_from='get_slug',
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_absolute_url = self.absolute_url if self.pk else ''

    def save(self, *args, **kwargs):
        """Save the model instance to the database."""
        if self.slug:
            # If the slug has changed, create a redirect.
            if self._state.adding:
                pass
            elif self.absolute_url != self._original_absolute_url:
                Redirect.objects.create(
                    old_path=self._original_absolute_url,
                    new_path=self.absolute_url,
                )
        else:
            # Set a slug automatically.
            self.slug = self.get_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Return the URL for the model instance detail page."""
        slug = getattr(self, 'slug', None)
        if self._state.adding and not slug:
            return ''
        return f'/{self._meta.app_label}/{slug or self.pk}'

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
        return self.absolute_url

    def get_detail_link(self, content: Optional[str] = None) -> SafeString:
        """Return a link to the model instance's detail page."""
        content = content or '<i class="fas fa-info-circle"></i>'
        return format_html(f'<a href="{self.detail_url}" target="_blank">{content}</a>')

    def get_slug(self) -> str:
        """Get a slug for the model instance."""
        slug = ''
        slug_base_fields = getattr(self, 'slug_base_fields', ['title'])
        for base_field in slug_base_fields:
            slug_base = str(getattr(self, base_field, ''))
            if not slug_base:
                continue
            elif '<' in slug_base:
                slug_base = soupify(slug_base).get_text()
            slug = slugify(slug_base)[:75]
        return slug or str(self.pk)
