"""Model classes for entity engagements, roles, affiliations, etc."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.dates.fields import HistoricDateTimeField
from apps.moderation.models.moderated_model.model import ModeratedModel
from core.fields.html_field import HTMLField
from core.models.relations.moderated import ModeratedRelation

MAX_NAME_LENGTH: int = 100


class _Engagement(ModeratedRelation):
    """An engagement with a beginning and, perhaps, an end."""

    start_date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for the _Engagement model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        abstract = True


class Affiliation(_Engagement):
    """An affiliation of entities."""

    entity = models.ForeignKey(
        to='entities.Entity',
        on_delete=models.CASCADE,
        related_name='affiliations',
        verbose_name=_('entity'),
    )
    affiliated_entity = models.ForeignKey(
        to='entities.Entity',
        on_delete=models.CASCADE,
        verbose_name=_('affiliated entity'),
    )
    roles = models.ManyToManyField(
        to='Role',
        related_name='affiliations',
        through='RoleFulfillment',
        blank=True,
        verbose_name=_('roles'),
    )

    class Meta:
        """Meta options for the Affiliation model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        unique_together = ['entity', 'affiliated_entity', 'start_date']

    def __str__(self) -> str:
        """Return the string representation of the affiliation."""
        return f'{self.entity} — {self.affiliated_entity}'


class Role(ModeratedModel):
    """A role fulfilled by an entity within an organization."""

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    description = HTMLField(blank=True)
    organization = models.ForeignKey(
        to='entities.Entity',
        related_name='roles',
        on_delete=models.CASCADE,
        verbose_name=_('organization'),
    )

    class Meta:
        """Meta options for the Role model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name = _('role')

    def __str__(self) -> str:
        """Return the role's string representation."""
        return self.name


class RoleFulfillment(_Engagement):
    """Fulfillment of a role by an entity."""

    affiliation = models.ForeignKey(
        to='entities.Affiliation',
        related_name='role_fulfillments',
        on_delete=models.CASCADE,
        verbose_name=_('affiliation'),
    )
    role = models.ForeignKey(
        to='entities.Role',
        related_name='fulfillments',
        on_delete=models.CASCADE,
        verbose_name=_('role'),
    )

    class Meta:
        """Meta options for the RoleFulfillment model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        unique_together = ['affiliation', 'role', 'start_date']
        verbose_name = _('role fulfillment')
