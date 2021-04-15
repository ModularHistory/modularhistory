"""Classes for models with related quotes."""

from django.contrib.contenttypes.fields import GenericRelation

from core.models.model import Model


class ModelWithRelatedQuotes(Model):
    """
    A model that has related quotes; e.g., an occurrence, topic, or person.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    quote_relations = GenericRelation('quotes.QuoteRelation')

    class Meta:
        """
        Meta options for ModelWithRelatedQuotes.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        abstract = True
