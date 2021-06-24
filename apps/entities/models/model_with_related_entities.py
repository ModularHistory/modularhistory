"""Classes for models with related entities."""

import re
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import ugettext_lazy as _

from core.models.model import ExtendedModel
from core.models.model_with_cache import store

if TYPE_CHECKING:
    from apps.entities.models.entity import Entity

ATTRIBUTE_NAMES = ('attributees', 'involved_entities', 'affiliated_entities')


class ModelWithRelatedEntities(ExtendedModel):
    """
    A model that has related entities (attributees, involved entities, etc.).

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    related_entities = models.ManyToManyField(
        to='entities.Entity',
        related_name='%(class)s_set',
        blank=True,
        verbose_name=_('related entities'),
    )

    class Meta:
        """Meta options for ModelWithRelatedEntities."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        abstract = True

    @property
    def _related_entities(self) -> 'QuerySet[Entity]':
        """Return the queryset of entities related to the model instance, or None."""
        for attribute_name in ATTRIBUTE_NAMES:
            attribute_value = getattr(self, attribute_name, None)
            if attribute_value:
                return attribute_value
        return self.related_entities.all()

    @property  # type: ignore
    @store(attribute_name='serialized_entities')
    def serialized_entities(self) -> list[dict]:
        """Return a list of dictionaries representing the instance's images."""
        return [entity.serialize() for entity in self._related_entities.all().iterator()]

    def preprocess_html(self, html: str) -> str:
        """Modify the value of an HTML field during cleaning."""
        # Wrap entity names in spans to identify them (so that links can be added if desired).
        entities = self.serialized_entities
        if entities:
            for entity in entities:
                aliases = entity.get('aliases') or []
                for name in set([entity['name']] + aliases):
                    opening_tag = (
                        f'<span class="entity-name" data-entity-id="{entity["slug"]}">'
                    )
                    closing_tag = '</span>'
                    html = re.sub(
                        # match instances not in quotations
                        rf'(^|^<p>|[^>])({name})(?:(?!\w|[^\ ]\"))',
                        rf'\g<1>{opening_tag}\g<2>{closing_tag}',
                        html,
                    )
        return html
