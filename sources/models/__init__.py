"""Public models of the sources app."""

from .affidavit import Affidavit, OldAffidavit
from .article import Article, OldArticle
from .book import Book, Chapter, OldBook, OldChapter, Section, SectionSource
from .citation import Citation
from .correspondence import Correspondence, Email, Letter, Memorandum, OldLetter
from .document import Collection, Document, DocumentSource, OldDocument, Repository
from .interview import Interview, OldInterview
from .journal import JournalEntry, OldJournalEntry
from .page_range import PageRange
from .piece import Essay, OldPiece, Piece
from .publication import Journal, Magazine, Newspaper, Publication
from .source import Source, TypedSource
from .source_attribution import SourceAttribution
from .source_containment import SourceContainment
from .source_file import SourceFile
from .spoken_source import Address, Discourse, Lecture, OldSpeech, Sermon, Speech, Statement, SpokenSource
from .textual_source import TextualSource
from .video_source import Documentary, OldDocumentary, OldVideoSource, VideoSource
from .webpage import OldWebPage, WebPage
