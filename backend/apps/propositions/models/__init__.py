"""Model classes of the propositions app, importable from `propositions.models`."""

from .argument import Argument, PremiseGroup, PremiseGroupInclusion
from .conflict import Conflict
from .fallacy import Fallacy, FallacyIdentification
from .occurrence import Occurrence, Publication
from .proposition import (
    TYPE_CHOICES,
    Citation,
    CollectionInclusion,
    Conclusion,
    EntityRelation,
    ImageRelation,
    Location,
    Proposition,
    QuoteRelation,
    TopicRelation,
)
from .support import ArgumentSupport
