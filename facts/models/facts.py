"""Model classes for facts."""

import re
import logging
from django.db.models import CASCADE, ForeignKey, ManyToManyField
from django.urls import reverse
from modularhistory.fields import HTMLField
from modularhistory.models import Model, PlaceholderGroups
from modularhistory.utils.html import escape_quotes
from facts.models.fact_relations import (
    EntityFactRelation,
    FactRelation,
    OccurrenceFactRelation,
    TopicFactRelation,
)
from topics.serializers import FactSerializer


class FactSupport(FactRelation):
    """TODO: add docstring."""

    supported_fact = ForeignKey(
        'facts.Fact', on_delete=CASCADE, related_name='supported_fact_supports'
    )
    supportive_fact = ForeignKey(
        'facts.Fact', on_delete=CASCADE, related_name='supportive_fact_supports'
    )

    class Meta:
        unique_together = ['supported_fact', 'supportive_fact']

    serializer = FactSerializer


class Fact(Model):
    """A fact."""

    text = HTMLField(unique=True)
    elaboration = HTMLField(null=True, blank=True)
    supportive_facts = ManyToManyField(
        'self', through=FactSupport, related_name='supported_facts', symmetrical=False
    )
    related_entities = ManyToManyField(
        'entities.Entity', through=EntityFactRelation, related_name='facts'
    )
    related_topics = ManyToManyField(
        'topics.Topic', through=TopicFactRelation, related_name='facts'
    )
    related_occurrences = ManyToManyField(
        'occurrences.Occurrence', through=OccurrenceFactRelation, related_name='facts'
    )

    searchable_fields = ['text']

    def __str__(self) -> str:
        """Return the fact's string representation."""
        return self.text.text

    @classmethod
    def get_object_html(
        cls, match: re.Match, use_preretrieved_html: bool = False
    ) -> str:
        """Return the obj's HTML based on a placeholder in the admin."""
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(PlaceholderGroups.PRERETRIEVED_HTML_GROUP)
            if preretrieved_html:
                return preretrieved_html.strip()
        fact = cls.get_object_from_placeholder(match)
        if isinstance(fact, dict):
            pk = fact['pk']
            text = fact['text']
            elaboration = fact['elaboration'] or ''
        else:
            pk = fact.pk
            text = fact.text.html
            elaboration = fact.elaboration.html if fact.elaboration else ''
        html = (
            f'<a href="{reverse("facts:detail", args=[pk])}" class="fact-link" '
            f'target="_blank" title="{escape_quotes(elaboration)}" '
            f'data-toggle="tooltip" data-html="true">{text}</a>'
        )
        logging.info(f'Retrieved fact HTML: {html}')
        return html
