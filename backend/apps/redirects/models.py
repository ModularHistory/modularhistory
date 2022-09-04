from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.redirects.tasks import write_map
from core.utils.sync import delay


class Redirect(models.Model):
    """A redirect from one URL path to another."""

    site = models.ForeignKey(Site, models.CASCADE, verbose_name=_('site'))
    old_path = models.CharField(
        _('redirect from'),
        max_length=200,
        db_index=True,
        validators=[RegexValidator(regex=r'^\/[-\w/\.\/]+$')],
        help_text=_('Example: /events/search/'),
    )
    new_path = models.CharField(
        _('redirect to'),
        max_length=200,
        blank=True,
        validators=[RegexValidator(regex=r'^\/[-\w/\.\/]+$')],
        help_text=_('Absolute path or full URL'),
    )

    class Meta:
        verbose_name = _('redirect')
        verbose_name_plural = _('redirects')
        unique_together = [['site', 'old_path']]
        ordering = ['old_path']

    def __str__(self) -> str:
        return f'{self.old_path} ---> {self.new_path}'

    def save(self, *args, **kwargs):
        """Save the redirect."""
        if not self.site:
            self.site = get_current_site()
        super().save(*args, **kwargs)
        # Re-write the redirects.map file.
        delay(write_map)
