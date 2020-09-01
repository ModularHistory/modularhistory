# type: ignore
# TODO: remove above line after fixing typechecking
from .article import Publication, Article, WebPage
from .base import (
    Source, SourceFile, SourceContainment,
    SourceAttribution
)
from .book import Book, Chapter
from .citation import Citation, PageRange
from .document import (
    Collection, Repository,
    Document, Affidavit,
    Letter, JournalEntry
)
from .piece import Piece
from .source_file import SourceFile
from .spoken import Speech, Interview, Documentary
