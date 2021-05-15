"""Classes for models with related quotes."""

from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext_lazy as _

from core.fields.sorted_m2m_field import SortedManyToManyField
from core.models.model import Model


class ModelWithRelatedQuotes(Model):
    """
    A model that has related quotes; e.g., an occurrence, topic, or person.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    related_quotes = SortedManyToManyField(
        to='quotes.Quote',
        related_name='%(class)s_set',
        blank=True,
        verbose_name=_('images'),
    )

    quote_relations = GenericRelation('quotes.QuoteRelation')

    class Meta:
        """Meta options for ModelWithRelatedQuotes."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True
