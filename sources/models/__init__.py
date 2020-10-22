"""Public models of the sources app."""

from .affidavit import Affidavit
from .article import Article
from .book import Book, Chapter, Section, SectionSource
from .citation import Citation
from .correspondence import Correspondence, Email, Letter, Memorandum
from .document import Collection, Document, DocumentSource, Repository
from .interview import Interview
from .journal import JournalEntry
from .page_range import PageRange
from .piece import Essay, Piece
from .publication import Journal, Magazine, Newspaper, Publication
from .source import Source
from .source_attribution import SourceAttribution
from .source_containment import SourceContainment
from .source_file import SourceFile
from .spoken_source import (
    Address,
    Discourse,
    Lecture,
    Sermon,
    Speech,
    Statement,
    SpokenSource,
)
from .textual_source import TextualSource
from .video_source import Documentary, VideoSource
from .webpage import WebPage
