"""All exposed model classes of the Facts app, importable from postulations.models."""

from .fact_relation import (
    EntityFactRelation,
    FactRelation,
    OccurrenceFactRelation,
    TopicFactRelation,
)
from .fact_support import PostulationSupport
from .postulation import Postulation
