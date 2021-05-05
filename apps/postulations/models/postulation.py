"""Model classes for postulations."""

import logging
import re
from typing import Match, Optional

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.model_with_sources import ModelWithSources
from apps.verifications.models import VerifiableModel
from core.fields import HTMLField
from core.fields.html_field import (
    OBJECT_PLACEHOLDER_REGEX,
    TYPE_GROUP,
    PlaceholderGroups,
)
from core.models import SluggedModel
from core.models.model import ModelSerializer
from core.utils.html import escape_quotes
from core.utils.string import dedupe_newlines, truncate

fact_placeholder_regex = OBJECT_PLACEHOLDER_REGEX.replace(
    TYPE_GROUP, rf'(?P<{PlaceholderGroups.MODEL_NAME}>postulation)'
)
logging.debug(f'Fact placeholder pattern: {fact_placeholder_regex}')


DEGREES_OF_CERTAINTY = (
    (0, 'No credible evidence'),
    (1, 'Some credible evidence'),
    (2, 'A preponderance of evidence'),
    (3, 'Beyond reasonable doubt'),
    (4, 'Beyond any shadow of a doubt'),
)


class PostulationSerializer(ModelSerializer):
    """Serializer for postulations."""

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of serialized postulations."""
        return 'topics.fact'


class Postulation(SluggedModel, VerifiableModel, ModelWithSources):
    """A postulation."""

    summary = HTMLField(
        verbose_name=_('statement'), unique=True, paragraphed=False, processed=False
    )
    elaboration = HTMLField(
        verbose_name=_('elaboration'), null=True, blank=True, paragraphed=True
    )
    certainty = models.PositiveSmallIntegerField(
        verbose_name=_('certainty'), choices=DEGREES_OF_CERTAINTY
    )
    supportive_facts = models.ManyToManyField(
        to='self',
        through='postulations.PostulationSupport',
        related_name='supported_postulations',
        symmetrical=False,
        verbose_name=_('supportive facts'),
    )
    related_entities = models.ManyToManyField(
        to='entities.Entity',
        through='postulations.EntityFactRelation',
        related_name='postulations',
        verbose_name=_('related entities'),
    )
    related_topics = models.ManyToManyField(
        to='topics.Topic',
        through='postulations.TopicFactRelation',
        related_name='postulations',
        verbose_name=_('related topics'),
    )
    related_occurrences = models.ManyToManyField(
        to='occurrences.Occurrence',
        through='postulations.OccurrenceFactRelation',
        related_name='postulations',
        verbose_name=_('related occurrences'),
    )

    searchable_fields = ['summary', 'elaboration']
    serializer = PostulationSerializer
    slug_base_field = 'summary'

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
                f'<a href="{reverse("postulations:detail", args=[self.pk])}" class="fact-link" '
                f'target="_blank" title="{escape_quotes(elaboration)}" '
                f'data-toggle="tooltip" data-html="true">{self.summary.html}</a>'
            )
        else:
            summary_link = (
                f'<a href="{reverse("postulations:detail", args=[self.pk])}" class="fact-link" '
                f'target="_blank">{self.summary.html}</a>'
            )
        return summary_link

    @classmethod
    def get_object_html(cls, match: Match, use_preretrieved_html: bool = False) -> str:
        """Return the obj's HTML based on a placeholder in the admin."""
        if not match:
            logging.error('fact.get_object_html was called without a match')
            raise ValueError
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(PlaceholderGroups.HTML)
            if preretrieved_html:
                return preretrieved_html.strip()
        fact: 'Postulation' = cls.objects.get(pk=match.group(PlaceholderGroups.PK))
        return fact.summary_link

    @classmethod
    def get_updated_placeholder(cls, match: Match) -> str:
        """Return a placeholder for a model instance depicted in an HTML field."""
        placeholder = match.group(0)
        logging.debug(f'Looking at {truncate(placeholder)}')
        extant_html: Optional[str] = match.group(PlaceholderGroups.HTML)
        extant_html = extant_html.strip() if extant_html else extant_html
        if extant_html:

            if '<a ' not in extant_html:
                html = cls.get_object_html(match)
                html = re.sub(
                    r'(.+?">).+?(<\/a>)',  # TODO
                    rf'\g<1>{extant_html}\g<2>',
                    html,
                )
                placeholder = placeholder.replace(
                    match.group(PlaceholderGroups.HTML), html
                )
            else:
                logging.info('Returning extant placeholder')
                return placeholder
        else:
            html = cls.get_object_html(match)
            model_name = match.group(PlaceholderGroups.MODEL_NAME)
            pk = match.group(PlaceholderGroups.PK)
            placeholder = f'[[ {model_name}: {pk}: {html} ]]'
        return dedupe_newlines(placeholder)
