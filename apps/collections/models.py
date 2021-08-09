from typing import TYPE_CHECKING

from django.db import models

from apps.search.models.searchable_model import SearchableModel
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.manager import SearchableManager
from django.conf import settings

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class AbstractCollectionInclusion(models.Model):
    """An inclusion of a model instance in a collection."""

    collection = ManyToManyForeignKey(
        to='collections.Collection', related_name='%(app_label)s_%(class)s_set'
    )

    class Meta:
        abstract = True


class CollectionManager(SearchableManager):
    """Manager class for collections."""

    def get_queryset(self) -> 'QuerySet[Collection]':
        return super().get_queryset().select_related('creator')


class Collection(SearchableModel):
    """A collection of model instances."""

    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name='collections',
    )

    entities = models.ManyToManyField(
        to='entities.Entity',
        through='entities.CollectionInclusion',
        related_name='collections',
        blank=True,
    )
    propositions = models.ManyToManyField(
        to='propositions.Proposition',
        through='propositions.CollectionInclusion',
        related_name='collections',
        blank=True,
    )

    objects: CollectionManager = CollectionManager()
    searchable_fields = ['title', 'creator__name']

    def __str__(self) -> str:
        """Return the model instance's string representation."""
        return f'{self.title} (by {self.creator})'
