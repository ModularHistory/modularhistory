"""Classes for models with related quotes."""

from typing import Type, Union

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.fields.custom_m2m_field import CustomManyToManyField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.model import Model
from core.models.positioned_relation import PositionedRelation


class AbstractQuoteRelation(PositionedRelation):
    """
    Abstract base model for quote relations.

    Models governing m2m relationships between `Quote` and another model
    should inherit from this abstract model.
    """

    quote = ManyToManyForeignKey(
        to='quotes.Quote', related_name='%(app_label)s_%(class)s_set'
    )

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for AbstractQuoteRelation."""

        abstract = True

    def content_object(self) -> models.ForeignKey:
        """Foreign key to the model that references the quote."""
        raise NotImplementedError


class RelatedQuotesField(CustomManyToManyField):
    """Custom field for related quotes."""

    target_model = 'quotes.Quote'
    through_model = AbstractQuoteRelation

    def __init__(self, through: Union[Type[AbstractQuoteRelation], str], **kwargs):
        """Construct the field."""
        kwargs['through'] = through
        kwargs['verbose_name'] = _('related quotes')
        super().__init__(**kwargs)


class ModelWithRelatedQuotes(Model):
    """A model that has related quotes; e.g., an occurrence, topic, or person."""

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for ModelWithRelatedQuotes."""

        abstract = True

    @property
    def related_quotes(self) -> RelatedQuotesField:
        """
        Require implementation of a `related_quotes` field on inheriting models.

        For example:
        ``
        related_quotes = RelatedQuotesField(through=QuoteRelation)
        ``
        """
        raise NotImplementedError

    @property
    def quote_relations(self):
        """
        Require the intermediate model to specify `related_name='quote_relations'`.

        Models inheriting from ModelWithRelatedQuotes must have a m2m relationship
        with the Quote model with a `through` model that inherits from
        AbstractQuoteRelation and uses `related_name='quote_relations'`.
        For example:

        ``
        class QuoteRelation(AbstractQuoteRelation):
            content_object = ManyToManyForeignKey(
                to='propositions.Proposition',
                related_name='quote_relations',
            )
        ``
        """
        raise NotImplementedError
