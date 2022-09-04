from typing import Optional

from autoslug import AutoSlugField
from django.conf import settings
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

    def clean(self):
        super().clean()
        if not self.slug:
            # Set a slug automatically.
            self.slug = self.get_slug()

    def pre_save(self):
        super().pre_save()
        self._original_slug = self.get_field_value_from_db('slug')

    def post_save(self):
        # If the slug has changed, create a redirect.
        original_slug = self._original_slug
        if original_slug and self.slug != original_slug:
            Redirect.objects.update_or_create(
                site_id=settings.SITE_ID,
                old_path=self.absolute_url.replace(self.slug, self._original_slug),
                defaults={'new_path': self.absolute_url},
            )
        # Delete any redirects that would hijack this model instance's new URL.
        Redirect.objects.filter(site_id=settings.SITE_ID, old_path=self.absolute_url).delete()

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
