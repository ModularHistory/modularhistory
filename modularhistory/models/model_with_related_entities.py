"""Classes for models with related entities."""

import re
from typing import Dict, List, Optional, TYPE_CHECKING

from django.db.models import QuerySet

from modularhistory.models import Model
from modularhistory.models.model_with_computations import retrieve_or_compute
from entities.serializers import EntitySerializer

if TYPE_CHECKING:
    from entities.models import Entity

ATTRIBUTE_NAMES = ('attributees', 'involved_entities', 'affiliated_entities')


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
        """Return the queryset of entities related to the model instance, or None."""
        for attribute_name in ATTRIBUTE_NAMES:
            attribute_value = getattr(self, attribute_name, None)
            if attribute_value:
                return attribute_value
        return None

    @property  # type: ignore
    @retrieve_or_compute(attribute_name='serialized_images')
    def serialized_entities(self) -> List[Dict]:
        """Return a list of dictionaries representing the instance's images."""
        return [
            EntitySerializer(image_relation.image).data
            for image_relation in self.image_relations.all().select_related('image')
        ]

    def preprocess_html(self, html: str) -> str:
        """Modify the value of an HTML field during cleaning."""
        # Wrap entity names in spans to identify them (so that links can be added if desired).
        entities = self.related_entities
        if entities and entities.exists():
            for entity in entities.all():  # TODO: use .iterator() ?
                ent: 'Entity' = entity
                aliases = ent.aliases or []
                for name in set([ent.name] + aliases):
                    opening_span_tag = (
                        f'<span class="entity-name" data-entity-id="{ent.pk}">'
                    )
                    closing_span_tag = '</span>'
                    html = re.sub(
                        # match instances not in quotations
                        rf'(^|^<p>|[^>])({name})(?:(?!\w|[^\ ]\"))',
                        rf'\g<1>{opening_span_tag}\g<2>{closing_span_tag}',
                        html,
                    )
        return html
