"""Classes for models with related quotes."""

from django.contrib.contenttypes.fields import GenericRelation

from modularhistory.models.model import Model


class ModelWithRelatedQuotes(Model):
    """
    A model that has related quotes; e.g., an occurrence, topic, or person.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    quote_relations = GenericRelation('quotes.QuoteRelation')

    class Meta:
        abstract = True

    # TODO: Do this check in forms rather than in the model, since there's already some bad data
    # if len(self.citations.filter(position=1)) > 1:
    #     raise ValidationError('Citation positions should be unique.')
