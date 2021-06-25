"""Model classes of the propositions app, importable from `propositions.models`."""

from .argument import Argument
from .conflict import Conflict
from .fallacy import Fallacy, FallacyIdentification
from .occurrence import Occurrence, Publication
from .proposition import (
    Citation,
    CollectionInclusion,
    Conclusion,
    ImageRelation,
    Location,
    Proposition,
    QuoteRelation,
)
from .support import ArgumentSupport
