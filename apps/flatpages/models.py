from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import NoReverseMatch, get_script_prefix, reverse
from django.utils.encoding import iri_to_uri
from django.utils.translation import gettext_lazy as _

from apps.moderation.models.moderated_model import ModeratedModel
from apps.redirects.models import Redirect
from core.fields.html_field import HTMLField

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

URL_PATH_PATTERN = r'\/[-\w/\.\/]+[^\/]'


class FlatPage(ModeratedModel):
    """A page of "flat" HTML content."""

    path = models.CharField(
        verbose_name=_('URL path'),
        max_length=100,
        db_index=True,
        validators=[RegexValidator(regex=rf'^{URL_PATH_PATTERN}$')],
        help_text=(
            'Example: “/about/contact”. Requires a leading slash and no trailing slash.'
        ),
    )
    title = models.CharField(verbose_name=_('title'), max_length=200)
    meta_description = models.TextField(
        verbose_name=_('meta description'),
        help_text=(
            "Content for the page's meta description, which is displayed "
            "underneath the page title on Google SERPs; should catch users' "
            'attention and increase and increase the click rate'
        ),
    )
    content = HTMLField(verbose_name=_('content'), blank=True)
    enable_comments = models.BooleanField(_('enable comments'), default=False)
    registration_required = models.BooleanField(
        verbose_name=_('registration required'),
        help_text=_(
            'If this is checked, only logged-in users will be able to view the page.'
        ),
        default=False,
    )
    sites = models.ManyToManyField(to=Site, verbose_name=_('sites'))

    class Meta:
        verbose_name = _('flat page')
        verbose_name_plural = _('flat pages')
        ordering = ['path']
        unique_together = ['path']

    class Moderation(ModeratedModel.Moderation):
        excluded_fields = ModeratedModel.Moderation.excluded_fields + ['sites']

    @classmethod
    def get_serializer(self):
        """Return the serializer for the entity."""
        from apps.flatpages.api.serializers import FlatPageSerializer

        return FlatPageSerializer

    def __str__(self) -> str:
        return f'{self.path} -- {self.title}'

    def clean(self):
        super().clean()
        path: str = self.path or ''
        if not path:
            raise ValidationError(f'URL path is not set for flatpage "{self.title}"')
        if not self.title:
            raise ValidationError(f'Title is not set for flatpage "{self.title}"')
        # Remove trailing slash.
        path = path.rstrip('/')
        pages_with_same_path = self.__class__.objects.filter(path=path)
        if self.pk:
            pages_with_same_path = pages_with_same_path.exclude(pk=self.pk)
            sites: 'QuerySet[Site]' = self.sites.all()
            if sites.exists() and pages_with_same_path.filter(sites__in=sites).exists():
                for site in sites:
                    if pages_with_same_path.filter(sites=site).exists():
                        raise ValidationError(
                            _('Page with path %(path)s already exists for site %(site)s'),
                            code='duplicate_path',
                            params={'path': path, 'site': site},
                        )

    def pre_save(self):
        super().pre_save()
        original_path = self.get_field_value_from_db('path')
        if original_path and self.path != original_path:
            Redirect.objects.create(
                old_path=original_path,
                new_path=self.path,
                site_id=settings.SITE_ID,
            )

    def get_absolute_url(self):
        from .views import flatpage

        for path in (self.path.lstrip('/'), self.path):
            try:
                return reverse(flatpage, kwargs={'path': path})
            except NoReverseMatch:
                pass
        # Handle script prefix manually because we bypass reverse()
        return iri_to_uri(get_script_prefix().rstrip('/') + self.path)
