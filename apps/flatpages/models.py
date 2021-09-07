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


class FlatPage(ModeratedModel):
    """A page of "flat" HTML content."""

    path = models.CharField(
        verbose_name=_('URL path'),
        max_length=100,
        db_index=True,
        validators=[RegexValidator(regex=r'^\/[-\w/\.\/]+\/$')],
        help_text=('Example: “/about/contact/”. Requires leading and trailing slashes.'),
    )
    title = models.CharField(verbose_name=_('title'), max_length=200)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_path = self.path

    def __str__(self):
        return f'{self.path} -- {self.title}'

    def pre_save(self):
        super().pre_save()
        if self.path != self._original_path:
            Redirect.objects.create(
                old_path=self._original_path,
                new_path=self.path,
                site_id=settings.SITE_ID,
            )

    def clean(self):
        """Prepare the flat page to be saved."""
        path = self.path
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
        super().clean()

    def get_absolute_url(self):
        from .views import flatpage

        for path in (self.path.lstrip('/'), self.path):
            try:
                return reverse(flatpage, kwargs={'path': path})
            except NoReverseMatch:
                pass
        # Handle script prefix manually because we bypass reverse()
        return iri_to_uri(get_script_prefix().rstrip('/') + self.path)
