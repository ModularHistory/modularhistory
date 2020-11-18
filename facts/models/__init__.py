"""All exposed model classes of the Facts app, importable from facts.models."""

from .fact import Fact, FactSupport
from .fact_relation import (
    EntityFactRelation,
    FactRelation,
    OccurrenceFactRelation,
    TopicFactRelation,
)
