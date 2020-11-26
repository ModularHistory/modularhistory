"""All exposed model classes of the Facts app, importable from facts.models."""

from .fact import Postulation
from .fact_relation import (
    EntityFactRelation,
    FactRelation,
    OccurrenceFactRelation,
    TopicFactRelation,
)
from .fact_support import PostulationSupport
