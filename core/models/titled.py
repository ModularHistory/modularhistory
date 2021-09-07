from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class TitledModel(models.Model):
    """Base model for models of which instances should have a title."""

    title = models.CharField(
        verbose_name=_('title'),
        max_length=120,
        blank=True,
        help_text=('This value can be used as a page header and/or title attribute.'),
    )

    class Meta:
        abstract = True

    def save(self, **kwargs):
        if not self.title:
            self.title = self.get_default_title()
        super().save(**kwargs)

    def clean(self):
        if not self.title:
            try:
                self.title = self.get_default_title()
            except NotImplementedError:
                raise ValidationError(f'Title must be set.')
        super().clean()

    def get_default_title(self) -> str:
        raise NotImplementedError
