from django.contrib.sites.models import Site
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Redirect(models.Model):
    site = models.ForeignKey(Site, models.CASCADE, verbose_name=_('site'))
    old_path = models.CharField(
        _('redirect from'),
        max_length=200,
        db_index=True,
        validators=[RegexValidator(regex=r'^\/[-\w/\.\/]+\/$')],
        help_text=_('Example: /events/search/'),
    )
    new_path = models.CharField(
        _('redirect to'),
        max_length=200,
        blank=True,
        help_text=_('Absolute path or full URL'),
    )

    class Meta:
        verbose_name = _('redirect')
        verbose_name_plural = _('redirects')
        unique_together = [['site', 'old_path']]
        ordering = ['old_path']

    def __str__(self):
        return f'{self.old_path} ---> {self.new_path}'
