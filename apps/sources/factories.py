import factory
from factory import fuzzy

from apps.moderation.factories import ModeratedModelFactory
from apps.places.factories import PlaceFactory
from apps.propositions.factories import PropositionFactory
from apps.sources import models
from apps.sources.models.mixins.page_numbers import PageNumbersMixin
from apps.sources.models.mixins.textual import TextualMixin
from core.factories import UniqueFaker


class SourceFileFactory(ModeratedModelFactory):
    class Meta:
        model = models.SourceFile

    file = factory.django.FileField()
    name = UniqueFaker('file_name')
    page_offset = fuzzy.FuzzyInteger(1, 500)
    first_page_number = fuzzy.FuzzyInteger(1, 250)
    uploaded_at = factory.Faker('date_time_this_month')


class SourceFactory(ModeratedModelFactory):
    class Meta:
        model = models.Source

    title = factory.Faker('sentence', nb_words=10)
    slug = factory.Faker('slug')
    date = factory.Faker('historic_datetime')
    end_date = factory.Faker('historic_datetime')
    url = factory.Faker('url')
    href = factory.Faker('url')
    location = factory.SubFactory(PlaceFactory)
    file = factory.SubFactory(SourceFileFactory)


class TextualSourceFactory(SourceFactory):
    class Meta:
        model = TextualMixin

    editors = factory.Faker('name')
    original_publication_date = factory.Faker('historic_datetime')


class PageNumberedSourceFactory(TextualSourceFactory):
    class Meta:
        model = PageNumbersMixin

    editors = factory.Faker('name')
    page_number = fuzzy.FuzzyInteger(1, 500)
    end_page_number = fuzzy.FuzzyInteger(500, 1000)


class SourceContainmentFactory(ModeratedModelFactory):
    class Meta:
        model = models.SourceContainment

    source = factory.SubFactory(SourceFactory)
    container = factory.SubFactory(SourceFactory)
    phrase = fuzzy.FuzzyChoice(
        x for x, y in models.SourceContainment.ContainmentPhrase.choices
    )
    page_number = fuzzy.FuzzyInteger(1, 500)
    end_page_number = fuzzy.FuzzyInteger(500, 1000)
    position = fuzzy.FuzzyInteger(1, 50)


class PublicationMixinFactory(ModeratedModelFactory):
    class Meta:
        model = models.AbstractPublication

    name = factory.Faker('company')
    aliases = [factory.Faker('company') for _ in range(2)]
    description = factory.Faker('sentence', nb_words=10)


class PublicationFactory(PublicationMixinFactory):
    class Meta:
        model = models.Publication

    type = fuzzy.FuzzyChoice(models.Publication._typedmodels_registry.keys())


class ArticleFactory(PageNumberedSourceFactory):
    class Meta:
        model = models.Article

    number = fuzzy.FuzzyInteger(1, 20)
    volume = fuzzy.FuzzyInteger(1, 10)
    publication = factory.SubFactory(PublicationFactory)


class BookFactory(TextualSourceFactory):
    class Meta:
        model = models.Book

    publisher = factory.Faker('company')
    translator = factory.Faker('name')
    edition_year = fuzzy.FuzzyInteger(1920, 2021)
    edition_number = fuzzy.FuzzyInteger(1, 20)
    volume_number = fuzzy.FuzzyInteger(1, 10)


class RepositoryFactory(ModeratedModelFactory):
    class Meta:
        model = models.Repository

    name = UniqueFaker('word')
    owner = factory.Faker('name')
    location = factory.SubFactory(PlaceFactory)


class CollectionFactory(ModeratedModelFactory):
    class Meta:
        model = models.Collection

    name = factory.Faker('sentence', nb_words=2)
    url = factory.Faker('url')
    repository = factory.SubFactory(RepositoryFactory)


class DocumentFactory(PageNumberedSourceFactory):
    class Meta:
        model = models.Document

    location_info = factory.Faker('address')
    collection = factory.SubFactory(CollectionFactory)
    collection_number = fuzzy.FuzzyInteger(1, 20)
    descriptive_phrase = factory.Faker('sentence', nb_words=3)
    information_url = factory.Faker('url')


class AffidavitFactory(DocumentFactory):
    class Meta:
        model = models.Affidavit

    certifier = factory.Faker('name')


class CorrespondenceFactory(DocumentFactory):
    class Meta:
        model = models.Correspondence

    type = fuzzy.FuzzyChoice(x[0] for x in models.CORRESPONDENCE_TYPES)
    recipient = factory.Faker('word')


class EntryFactory(PageNumberedSourceFactory):
    class Meta:
        model = models.Entry


class FilmFactory(SourceFactory):
    class Meta:
        model = models.Film

    type = fuzzy.FuzzyChoice(x[0] for x in models.FILM_TYPES)


class InterviewFactory(SourceFactory):
    class Meta:
        model = models.Interview

    interviewers = factory.Faker('name')


class PieceFactory(PageNumberedSourceFactory):
    class Meta:
        model = models.Piece


class WebsiteFactory(PublicationMixinFactory):
    class Meta:
        model = models.Website

    owner = factory.Faker('company')


class WebpageFactory(TextualSourceFactory):
    class Meta:
        model = models.Webpage

    website_name = factory.Faker('company')
    website = factory.SubFactory(WebsiteFactory)


class ReportFactory(TextualSourceFactory):
    class Meta:
        model = models.Report

    publisher = factory.Faker('company')
    number = fuzzy.FuzzyInteger(1, 20)


class SpeechFactory(SourceFactory):
    class Meta:
        model = models.Speech

    type = fuzzy.FuzzyChoice(x[0] for x in models.SPEECH_TYPES)
    audience = factory.Faker('name')
    utterance = factory.SubFactory(PropositionFactory, type='speech')
