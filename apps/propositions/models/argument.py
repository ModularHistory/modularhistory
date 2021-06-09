import logging

from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from core.fields.html_field import HTMLField
from core.models.positioned_relation import PositionedRelation
from core.utils.html import soupify

TYPE_CHOICES = (
    (None, '-------'),
    (1, 'deductive'),
    (2, 'inductive'),
)


class Argument(PositionedRelation):
    """An argument for a proposition."""

    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES,
        db_index=True,
        null=True,
    )
    premises = models.ManyToManyField(
        to='propositions.Proposition',
        through='propositions.ArgumentSupport',
        through_fields=('argument', 'premise'),
        related_name='supported_arguments',
        symmetrical=False,
        verbose_name=_('premises'),
    )
    conclusion = models.ForeignKey(
        to='propositions.Proposition',
        on_delete=models.CASCADE,
        related_name='arguments',
        verbose_name=_('conclusion'),
    )
    explanation = HTMLField(
        verbose_name=_('explanation'),
        paragraphed=True,
        processed=False,
        blank=True,
    )

    def __str__(self) -> str:
        """Return the proposition's string representation."""
        return f'Argument {self.number} for "{self.conclusion}"'

    @property
    def __html__(self) -> SafeString:
        """Return the proposition's string representation."""
        html = ''
        if not self._state.adding:
            try:
                _item = '<li>{}</li>'.format
                html = (
                    (
                        '<ol>'
                        f'{"".join([_item(str(premise)) for premise in self.premises.all()])}'
                        '</ol>'
                    )
                    if self.premises.exists()
                    else ''
                )
            except Exception as err:
                logging.info(err)
        return format_html(html)
