from typing import Any  # , TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation

from history.models.base_model import BaseModel


# if TYPE_CHECKING:
#     from quotes.models import QuoteRelation


class RelatedQuotesMixin(BaseModel):
    related_quotes2: Any

    quote_relations = GenericRelation('quotes.QuoteRelation')

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        # TODO: Do this check in forms rather than in the model, since there's already some bad data
        # if len(self.citations.filter(position=1)) > 1:
        #     raise ValidationError('Citation positions should be unique.')
