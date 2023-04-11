import os
from typing import List, Optional
from dataclasses import dataclass
import glob

from langchain.indexes import VectorstoreIndexCreator

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

from .consts import WILDCARDS
from .console import console


class MultipleTextLoader(BaseLoader):
    """Load text files."""

    def __init__(self, path: str, wildcards: List[str], encoding: Optional[str] = None):
        """Initialize with file path."""
        self.path = path
        self.encoding = encoding
        self.wildcards = wildcards

    def _get_files_by_wildcards(self, path: str, wildcards: List[str]) -> List[str]:
        matched_files = []

        for wc in wildcards:
            pattern = os.path.join(path, "**", wc)
            matched_files.extend(glob.glob(pattern, recursive=True))

        return matched_files

    def load(self) -> List[Document]:
        """Load from file path."""
        documents = []
        for file_path in self._get_files_by_wildcards(self.path, self.wildcards):
            console.log(f"Adding: [blue underline]{file_path}", "…")
            with open(file_path, encoding=self.encoding) as f:
                text = f.read()
            metadata = {"source": file_path}
            documents.append(Document(page_content=text, metadata=metadata))
        return documents


@dataclass
class QueryResult:
    question: str
    answer: str
    sources: str


class RepositoryIndex:
    def __init__(self, path: str):
        self.path = path
        self.index = None

    def ingest(self):
        code_loader = MultipleTextLoader(self.path, WILDCARDS)

        with console.status(
            f"Ingesting code repository from path: [blue underline]{self.path}…",
            spinner="weather",
        ):
            self.index = VectorstoreIndexCreator().from_loaders([code_loader])

    def query_with_sources(self, query: str) -> QueryResult:
        with console.status("Querying…", spinner="weather"):
            return QueryResult(**self.index.query_with_sources(query))
