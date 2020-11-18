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
from modularhistory.models import Model, PlaceholderGroups
from modularhistory.utils.html import escape_quotes
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

    summary = HTMLField(unique=True, paragraphed=False)
    elaboration = HTMLField(null=True, blank=True, paragraphed=True)
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

    searchable_fields = ['summary', 'elaboration']

    def __str__(self) -> str:
        """Return the fact's string representation."""
        return self.summary.text

    @property
    def summary_link(self) -> str:
        """Return an HTML link to the fact, containing the summary text."""
        add_elaboration_tooltip = False
        elaboration = self.elaboration.html if self.elaboration else ''
        elaboration = elaboration.replace('\n', '')
        if add_elaboration_tooltip:
            summary_link = (
                f'<a href="{reverse("facts:detail", args=[self.pk])}" class="fact-link" '
                f'target="_blank" title="{escape_quotes(elaboration)}" '
                f'data-toggle="tooltip" data-html="true">{self.summary.html}</a>'
            )
        else:
            summary_link = (
                f'<a href="{reverse("facts:detail", args=[self.pk])}" class="fact-link" '
                f'target="_blank">{self.summary.html}</a>'
            )
        return summary_link

    @classmethod
    def get_object_html(
        cls, match: re.Match, use_preretrieved_html: bool = False
    ) -> str:
        """Return the obj's HTML based on a placeholder in the admin."""
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(PlaceholderGroups.HTML)
            if preretrieved_html:
                return preretrieved_html.strip()
        fact: 'Fact' = cls.get_object_from_placeholder(match)
        return fact.summary_link

    @classmethod
    def get_updated_placeholder(cls, match: re.Match) -> str:
        """Return a placeholder for a model instance depicted in an HTML field."""
        placeholder = match.group(0)
        logging.info(f'Getting updated fact placeholder for {placeholder}...')
        if match.group(PlaceholderGroups.HTML):
            html = match.group(PlaceholderGroups.HTML)
            if '<a ' not in html:
                fact_html = cls.get_object_html(match)
                fact_html = re.sub(
                    r'(.+?">).+?(<\/a>)',  # TODO
                    rf'\g<1>{html}\g<2>',
                    fact_html,
                )
                placeholder = placeholder.replace(
                    match.group(PlaceholderGroups.HTML), fact_html
                )
            return placeholder
        appendage = match.group(PlaceholderGroups.APPENDAGE)
        updated_appendage = f': {cls.get_object_html(match)}'
        if appendage:
            # TODO: preserve capitalization, etc.
            updated_placeholder = placeholder.replace(appendage, updated_appendage)
        else:
            updated_placeholder = (
                f'{re.sub(r" ?(?:>>|&gt;&gt;)", "", placeholder)}{updated_appendage} >>'
            )
        return updated_placeholder.replace('\n\n\n', '\n').replace('\n\n', '\n')
