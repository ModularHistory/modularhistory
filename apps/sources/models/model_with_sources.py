"""Classes for models with relations to sources."""

import logging
from typing import Optional, Type, Union

from celery import shared_task
from concurrency.fields import IntegerVersionField
from django.apps import apps
from django.db.models.fields.related import ManyToManyField
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.citation import AbstractCitation
from core.constants.strings import EMPTY_STRING
from core.fields import HTMLField
from core.fields.custom_m2m_field import CustomManyToManyField
from core.models.model import Model
from core.models.model_with_cache import retrieve_or_compute


class SourcesField(CustomManyToManyField):
    """Field for sources."""

    through_model = AbstractCitation

    def __init__(self, through: Union[Type[AbstractCitation], str], **kwargs):
        kwargs['to'] = 'sources.Source'
        kwargs['through'] = through
        kwargs['verbose_name'] = _('sources')
        super().__init__(**kwargs)


class ModelWithSources(Model):
    """
    A model that has sources; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but due to Django's model magic,
    it must be defined as an abstract model class.
    """

    version = IntegerVersionField()

    # Admin-facing notes (not to be displayed to users)
    notes = HTMLField(
        null=True, blank=True, paragraphed=True, processed=False, verbose_name=_('note')
    )

    class Meta:
        abstract = True

    @property
    def cached_citations(self) -> list:
        """Return the model instance's cached citations."""
        citations = self.cache.get('citations', [])
        if citations or not self.sources.exists():
            return citations
        citations = [citation.serialize() for citation in self.citations.all()]
        cache_citations.delay(
            f'{self.__class__._meta.app_label}.{self.__class__.__name__.lower()}',
            self.id,
            citations,
        )
        return citations

    @property
    def citations(self):
        """
        The `related_name` value for the intermediate citation model.

        Models inheriting from ModelWithSources must have a m2m relationship
        with the Source model with a `through` model that inherits from
        AbstractCitation and uses `related_name='citations'`. For example:

        ``
        class Citation(AbstractCitation):
            content_object = ManyToManyForeignKey(
                to='propositions.Proposition',
                related_name='citations',
            )
        ``
        """
        citations = getattr(self, 'new_citations', None)
        if citations:
            return citations
        raise NotImplementedError(
            f'{self.__class__} lacks an associated `Citation` model '
            'with related_name="citations"'
        )

    @property
    def sources(self) -> ManyToManyField:
        raise NotImplementedError

    @property
    def source_file_url(self) -> Optional[str]:
        """TODO: write docstring."""
        if self.citation:
            return self.citation.source_file_url
        return None

    @property
    def citation(self) -> Optional[AbstractCitation]:
        """Return the quote's primary citation, if a citation exists."""
        try:
            return self.citations.order_by('position')[0]
        except IndexError:
            return None

    @property
    def citation_html(self) -> SafeString:
        """Return the instance's full citation HTML."""
        try:
            citation_html = '; '.join(
                citation.get('html') for citation in self.cached_citations
            )
        except Exception as error:
            logging.error(f'{error}')
            citation_html = EMPTY_STRING
        return format_html(citation_html)


@shared_task
def cache_citations(model: str, instance_id: int, citations: list):
    """Save cached citations to a model instance."""
    if not citations:
        return
    Model = apps.get_model(model)
    model_instance: ModelWithSources = Model.objects.get(pk=instance_id)  # noqa: N806
    model_instance.cache['citations'] = citations
    model_instance.save(wipe_cache=False)
