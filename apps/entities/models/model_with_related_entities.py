"""Classes for models with related entities."""

import re
from typing import TYPE_CHECKING, Union

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import ugettext_lazy as _

from core.fields.custom_m2m_field import CustomManyToManyField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.model import ExtendedModel
from core.models.model_with_cache import store
from core.models.relations.moderated import ModeratedRelation

if TYPE_CHECKING:
    from apps.entities.models.entity import Entity

ATTRIBUTE_NAMES = ('attributees', 'involved_entities', 'affiliated_entities')


class AbstractEntityRelation(ModeratedRelation):
    """
    Abstract base model for entity relations.

    Models governing m2m relationships between `Entity` and another model
    should inherit from this abstract model.
    """

    entity = ManyToManyForeignKey(
        to='entities.Entity',
        related_name='%(app_label)s_%(class)s_set',
        verbose_name=_('related entity'),
    )

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self.entity}'

    def content_object(self) -> models.ForeignKey:
        """Foreign key to the model that references the entity."""
        raise NotImplementedError


class RelatedEntitiesField(CustomManyToManyField):
    """Custom field for related entities."""

    target_model = 'entities.Entity'
    through_model_base = AbstractEntityRelation

    def __init__(self, through: Union[type[AbstractEntityRelation], str], **kwargs):
        """Construct the field."""
        kwargs['through'] = through
        kwargs['verbose_name'] = _('related entities')
        super().__init__(**kwargs)


class ModelWithRelatedEntities(ExtendedModel):
    """
    A model that has related entities (attributees, involved entities, etc.).

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    @property
    def related_entities(self) -> RelatedEntitiesField:
        """
        Require implementation of a `entities` field on inheriting models.

        For example:
        ``
        related_entities = RelatedEntitiesField(through=EntityRelation)
        ``
        """
        raise NotImplementedError

    @property
    def _related_entities(self) -> 'QuerySet[Entity]':
        """Return the queryset of entities related to the model instance, or None."""
        for attribute_name in ATTRIBUTE_NAMES:
            attribute_value = getattr(self, attribute_name, None)
            if attribute_value:
                return attribute_value
        return self.related_entities.all()

    @property  # type: ignore
    @store(key='serialized_entities')
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
