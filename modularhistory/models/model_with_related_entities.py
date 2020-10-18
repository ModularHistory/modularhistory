"""Classes for models with related entities."""

import re
from typing import Optional, TYPE_CHECKING

from django.db.models import QuerySet

from modularhistory.models.model import Model

if TYPE_CHECKING:
    from entities.models import Entity

ATTRIBUTE_NAMES = (
    'attributees',
    'involved_entities',
    'affiliated_entities'
)


class ModelWithRelatedEntities(Model):
    """
    A model that has related entities (attributees, involved entities, etc.).

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    class Meta:
        abstract = True

    @property
    def related_entities(self) -> Optional['QuerySet[Entity]']:
        """Returns the queryset of entities related to the model instance, or None."""
        for attribute_name in ATTRIBUTE_NAMES:
            attribute_value = getattr(self, attribute_name, None)
            if attribute_value:
                return attribute_value
        return None

    def preprocess_html(self, html: str) -> str:
        """Modify the value of an HTML field during cleaning."""
        # Wrap entity names in spans to identify them (so that links can be added if desired).
        entities = self.related_entities
        if entities and entities.exists():
            entities = entities.all()
            for entity in entities:
                ent: 'Entity' = entity
                aliases = ent.aliases or []
                for name in set([ent.name] + aliases):
                    opening_span_tag = f'<span class="entity-name" data-entity-id="{ent.pk}">'
                    closing_span_tag = '</span>'
                    html = re.sub(
                        # match instances not in quotations
                        rf'(^|^<p>|[^>])({name})(?:(?!\w|[^\ ]\"))',
                        rf'\g<1>{opening_span_tag}\g<2>{closing_span_tag}',
                        html
                    )
        return html
