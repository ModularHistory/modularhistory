from django.db import models

from core.fields.m2m_foreign_key import ManyToManyForeignKey


class AbstractCollectionInclusion(models.Model):
    """An inclusion of a model instance in a collection."""

    collection = ManyToManyForeignKey(
        to='collections.Collection', related_name='%(app_label)s_%(class)s_set'
    )

    class Meta:
        abstract = True


class Collection(models.Model):
    """A collection of model instances."""

    creator = models.ForeignKey(
        to='users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name='collections',
    )

    def __str__(self) -> str:
        return f'collection created by {self.creator}'
