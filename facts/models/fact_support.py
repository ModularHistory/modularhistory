"""Model classes for facts."""

import logging
import re

from django.db.models import CASCADE, ForeignKey, ManyToManyField
from django.urls import reverse

from facts.models.fact_relation import (
    EntityFactRelation,
    FactRelation,
    OccurrenceFactRelation,
    TopicFactRelation,
)
from modularhistory.fields import HTMLField
from modularhistory.models.model import PlaceholderGroups
from modularhistory.utils.html import escape_quotes
from topics.serializers import FactSerializer
from verification.models import VerifiableModel


class FactSupport(FactRelation):
    """A supportion of a fact by another fact."""

    supported_fact = ForeignKey(
        'facts.Fact', on_delete=CASCADE, related_name='supported_fact_supports'
    )
    supportive_fact = ForeignKey(
        'facts.Fact', on_delete=CASCADE, related_name='supportive_fact_supports'
    )
