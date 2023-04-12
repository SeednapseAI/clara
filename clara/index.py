import os
import pathlib
import hashlib
from typing import List, Optional
from dataclasses import dataclass
import glob

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

from .consts import WILDCARDS, BASE_PERSIST_PATH
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
        self.index = VectorstoreIndexCreator().from_loaders([code_loader])

    def query_with_sources(self, query: str) -> QueryResult:
        return QueryResult(**self.index.query_with_sources(query))


class RepositoryIndexPersisted:
    def __init__(self, path: str):
        self.path = pathlib.Path(path).resolve()
        self.index = None

        self.persist_path = self.get_persist_path()

    def get_persist_path(self) -> str:
        hashed_path = hashlib.sha256(str(self.path).encode("utf-8")).hexdigest()
        short_hash = hashed_path[:8]

        base_name = os.path.basename(self.path)

        return os.path.join(BASE_PERSIST_PATH, f"{base_name}_{short_hash}")

    def ingest(self):
        console.log("Create persist directory:", self.persist_path)
        pathlib.Path(self.persist_path).mkdir(parents=True, exist_ok=True)
        console.log("Done! :check:")

        code_loader = MultipleTextLoader(self.path, WILDCARDS)
        self.index = VectorstoreIndexCreator(
            vectorstore_kwargs={"persist_directory": self.persist_path}
        ).from_loaders([code_loader])

    def persist(self):
        self.index.vectorstore.persist()

    def load(self) -> bool:
        if not os.path.exists(self.persist_path):
            return False

        vectorstore = Chroma(
            persist_directory=self.persist_path,
            embedding_function=OpenAIEmbeddings(),
        )
        self.index = VectorStoreIndexWrapper(vectorstore=vectorstore)

        return True

    def query_with_sources(self, query: str) -> QueryResult:
        return QueryResult(**self.index.query_with_sources(query))
