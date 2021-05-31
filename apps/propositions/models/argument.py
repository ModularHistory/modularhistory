from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.fields.html_field import HTMLField
from core.models.model import Model

TYPE_CHOICES = (
    (None, '-------'),
    (1, 'deductive'),
    (2, 'inductive'),
)


class Argument(Model):
    """An argument for a proposition."""

    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES,
        db_index=True,
        null=True,
    )
    premises = models.ManyToManyField(
        to='propositions.PolymorphicProposition',
        through='propositions.ArgumentSupport',
        through_fields=('argument', 'premise'),
        related_name='supported_arguments',
        symmetrical=False,
        verbose_name=_('premises'),
    )
    conclusion = models.ForeignKey(
        to='propositions.PolymorphicProposition',
        on_delete=models.CASCADE,
        related_name='arguments',
        verbose_name=_('conclusion'),
    )
    explanation = HTMLField(
        verbose_name=_('explanation'),
        paragraphed=True,
        processed=False,
    )

    def __str__(self) -> str:
        """Return the proposition's string representation."""
        premises = '\n + '.join(str(self.premises.all()))
        return f'{premises}\n --> {self.conclusion}'
