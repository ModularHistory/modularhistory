import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from core.fields.html_field import HTMLField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.positioned_relation import PositionedRelation
from core.utils.html import soupify

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

TYPE_CHOICES = (
    (None, '-------'),
    (1, 'deductive'),
    (2, 'inductive'),
)


class PremiseGroupInclusion(PositionedRelation):
    """A relation of a premise and a premise group."""

    premise_group = ManyToManyForeignKey(to='propositions.PremiseGroup')
    premise = ManyToManyForeignKey(to='propositions.Proposition')


class PremiseGroup(PositionedRelation):
    """A group of premises that, combined, support an argument."""

    type = models.CharField(
        max_length=3,
        choices=(('all', 'all'), ('any', 'any')),
        default='all',
    )
    premises = models.ManyToManyField(
        to='propositions.Proposition',
        through='propositions.PremiseGroupInclusion',
        verbose_name=_('premises'),
    )
    argument = models.ForeignKey(
        to='propositions.Argument',
        on_delete=models.CASCADE,
        related_name='premise_groups',
        verbose_name=_('argument'),
    )

    def __str__(self) -> str:
        newline = '\n'
        return f'{self.type}: \n{newline.join([str(premise) for premise in self.premises.all()])}'


class Argument(PositionedRelation):
    """An argument for a proposition."""

    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES,
        db_index=True,
        null=True,
    )
    premise_groups: 'RelatedManager[PremiseGroup]'
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

    class Meta:
        unique_together = ['position', 'conclusion']

    def __str__(self) -> str:
        """Return the proposition's string representation."""
        return f'Argument {self.number} for "{self.conclusion}"'

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
