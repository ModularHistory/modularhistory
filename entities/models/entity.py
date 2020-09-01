# type: ignore
# TODO: remove above line after fixing typechecking
from datetime import datetime
from typing import Optional

from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE, SET_NULL
from django.template.defaultfilters import truncatechars_html
from django.utils.safestring import SafeText, mark_safe

from history.fields import ArrayField, HistoricDateTimeField, HTMLField
from history.models import (
    Model, TaggableModel, TypedModel,
    RelatedQuotesMixin
)
from history.structures import HistoricDateTime
from images.models import Image
from .classification import Classification


class EntityImage(Model):
    entity = ForeignKey('Entity', related_name='entity_images', on_delete=CASCADE)
    image = ForeignKey(Image, related_name='image_entities', on_delete=CASCADE)

    class Meta:
        unique_together = ['entity', 'image']

    def __str__(self):
        return f'{self.image} ({self.image.id}) --> {self.entity} ({self.entity.id})'


parts_of_speech = (
    ('noun', 'noun'),
    ('adj', 'adjective'),
    ('any', 'noun / adjective'),
)


class EntityClassification(Model):
    entity = ForeignKey(
        'Entity', related_name='entity_classifications',
        on_delete=CASCADE
    )
    classification = ForeignKey(
        Classification, related_name='entity_classifications',
        on_delete=CASCADE
    )
    date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['entity', 'classification']

    def __str__(self):
        return str(self.classification)

    @property
    def weight(self) -> int:
        return self.classification.weight


class Entity(TypedModel, TaggableModel, RelatedQuotesMixin):
    """An entity"""
    name = models.CharField(max_length=100, unique=True)
    verbose_name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    aliases = ArrayField(
        models.CharField(max_length=100),
        null=True, blank=True
    )
    birth_date = HistoricDateTimeField(null=True, blank=True)
    death_date = HistoricDateTimeField(null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    classifications = ManyToManyField(
        Classification,
        related_name='entities',
        through='entities.EntityClassification',
        blank=True
    )
    images = ManyToManyField(
        Image,
        through='entities.EntityImage',
        related_name='entities',
        blank=True
    )
    affiliated_entities = ManyToManyField(
        'self',
        through='entities.Affiliation',
        blank=True
    )

    searchable_fields = ['name', 'aliases', 'description']

    class Meta:
        verbose_name_plural = 'Entities'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'

    @property
    def image(self) -> Optional[Image]:
        return (self.images.first() if self.images.exists()
                else None)

    @property
    def has_quotes(self) -> bool:
        return bool(len(self.quotes.all()))

    @property
    def description__truncated(self) -> SafeText:
        return mark_safe(truncatechars_html(self.description, 1200))

    def clean(self):
        super().clean()
        if not self.verbose_name:
            self.verbose_name = self.name

    def get_classification(self, date: HistoricDateTime) -> Optional['EntityClassification']:
        if not self.classifications.exists():
            return None
        classifications = EntityClassification.objects.filter(entity=self, date__lte=date)
        if not len(classifications):
            classifications = self.entity_classifications.all()
        classification = classifications.order_by('date', 'classification__weight').last()
        return classification

    def get_classification_string(
            self, date: HistoricDateTime
    ) -> Optional[str]:
        """Intelligently build a classification string, like `conservative LDS apostle`."""
        if not self.classifications.exists():
            return None
        words = []
        entity_classifications = EntityClassification.objects.filter(entity=self)
        entity_classifications = entity_classifications.exclude(date__gt=date) if date else entity_classifications

        noun_classifications = entity_classifications.filter(classification__part_of_speech='noun')
        if noun_classifications.exists():
            noun = noun_classifications.order_by('classification__weight', 'date').last()
            words += str(noun).split(' ')

        noun_adj_classifications = entity_classifications.filter(classification__part_of_speech='any')
        if noun_adj_classifications.exists():
            noun_adj = noun_adj_classifications.order_by('classification__weight', 'date').last()
            words = [word for word in str(noun_adj).split(' ') if word not in words] + words

        adj_classifications = entity_classifications.filter(classification__part_of_speech='adj')
        if adj_classifications.exists():
            adj = adj_classifications.order_by('classification__weight', 'date').last()
            words = [word for word in str(adj).split(' ') if word not in words] + words

        # Final removal of duplicate words
        words = list(dict.fromkeys(words))
        return ' '.join(words)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Person(Entity):
    """A person"""
    class Meta:
        verbose_name_plural = 'People'


class Deity(Entity):
    """A deity"""
    class Meta:
        verbose_name_plural = 'Deities'


class Group(Entity):
    pass


class Organization(Entity):
    """An organization"""
    parent_organization = ForeignKey(
        'self',
        related_name='child_organizations',
        null=True, blank=True,
        on_delete=SET_NULL
    )

    class Meta:
        verbose_name_plural = 'Organizations'

    @property
    def founding_date(self) -> datetime:
        return self.birth_date


class _Engagement(Model):
    start_date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Affiliation(_Engagement):
    entity = ForeignKey(Entity, related_name='affiliations', on_delete=CASCADE)
    affiliated_entity = ForeignKey(Entity, on_delete=CASCADE)
    roles = ManyToManyField(
        'Role', related_name='affiliations',
        through='RoleFulfillment',
        blank=True
    )

    class Meta:
        unique_together = ['entity', 'affiliated_entity', 'start_date']

    def __str__(self):
        return f'{self.entity} — {self.affiliated_entity}'


class Role(Model):
    name = models.CharField(max_length=100, unique=True)
    description = HTMLField(null=True, blank=True)
    organization = ForeignKey('Entity', related_name='roles', on_delete=CASCADE)

    def __str__(self):
        return self.name


class RoleFulfillment(_Engagement):
    affiliation = ForeignKey(Affiliation, related_name='role_fulfillments', on_delete=CASCADE)
    role = ForeignKey(Role, related_name='fulfillments', on_delete=CASCADE)

    class Meta:
        unique_together = ['affiliation', 'role', 'start_date']


class EntityIdea(Model):
    entity = ForeignKey(Entity, on_delete=CASCADE, related_name='entity_ideas')
    idea = ForeignKey('Idea', on_delete=CASCADE, related_name='entity_ideas')

    class Meta:
        unique_together = ['entity', 'idea']


class Idea(Model):
    name = models.CharField(max_length=100, unique=True)
    description = HTMLField(null=True, blank=True)
    promoters = ManyToManyField(Entity, related_name='ideas', blank=True)
    # related_ideas = ManyToManyField('self', )
