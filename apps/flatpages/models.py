from typing import TYPE_CHECKING

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import NoReverseMatch, get_script_prefix, reverse
from django.utils.encoding import iri_to_uri
from django.utils.translation import gettext_lazy as _

from apps.moderation.models.moderated_model import ModeratedModel

# from apps.redirects.models import Redirect
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
        ordering = ['url']
        unique_together = ['url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_path = self.path

    def __str__(self):
        return f'{self.url} -- {self.title}'

    def save(self, **kwargs):
        """Save the flat page to the db."""
        # if self.path != self._original_path:
        #     try:
        #         Redirect.objects.create(
        #             old_path=self._original_path,
        #             new_path=self.path,
        #             site=settings.SITE_ID,
        #         )
        #     except Exception as err:
        #         logging.error(err)
        return super().save(**kwargs)

    def clean(self):
        url = self.url
        pages_with_same_url = self.__class__.objects.filter(url=url)
        if self.pk:
            pages_with_same_url = pages_with_same_url.exclude(pk=self.pk)
            sites: 'QuerySet[Site]' = self.sites.all()
            if sites.exists() and pages_with_same_url.filter(sites__in=sites).exists():
                for site in sites:
                    if pages_with_same_url.filter(sites=site).exists():
                        raise ValidationError(
                            _('Flat page with url %(url)s already exists for site %(site)s'),
                            code='duplicate_url',
                            params={'url': url, 'site': site},
                        )
        super().clean()

    def get_absolute_url(self):
        from .views import flatpage

        for url in (self.url.lstrip('/'), self.url):
            try:
                return reverse(flatpage, kwargs={'url': url})
            except NoReverseMatch:
                pass
        # Handle script prefix manually because we bypass reverse()
        return iri_to_uri(get_script_prefix().rstrip('/') + self.url)
