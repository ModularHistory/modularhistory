"""Public models of the sources app."""

from .citation import Citation
from .publication import Journal, Magazine, Newspaper, Publication
from .source import PolymorphicSource
from .source_attribution import SourceAttribution
from .source_containment import SourceContainment
from .source_file import SourceFile
from .sources.affidavit import PolymorphicAffidavit
from .sources.article import PolymorphicArticle
from .sources.book import PolymorphicBook, PolymorphicSection
from .sources.correspondence import PolymorphicCorrespondence
from .sources.document import Collection, PolymorphicDocument, Repository
from .sources.film import Film
from .sources.interview import PolymorphicInterview
from .sources.journal import PolymorphicJournalEntry
from .sources.piece import PolymorphicPiece
from .sources.speech import PolymorphicSpeech
from .sources.webpage import PolymorphicWebPage, Website
