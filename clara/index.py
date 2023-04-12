import os
import pathlib
import hashlib
from typing import List
from dataclasses import dataclass
import glob

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

from .consts import WILDCARDS, BASE_PERSIST_PATH
from .console import console


@dataclass
class QueryResult:
    question: str
    answer: str
    sources: str


class RepositoryIndex:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.index = None

    def _get_texts(self):
        def get_files_by_wildcards(path: str, wildcards: List[str]) -> List[str]:
            matched_files = []

            for wc in wildcards:
                pattern = os.path.join(path, "**", wc)
                matched_files.extend(glob.glob(pattern, recursive=True))

            return matched_files

        documents = []
        for file_path in get_files_by_wildcards(self.path, WILDCARDS):
            console.log(f"Loading [blue underline]{file_path}", "…")
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load_and_split())

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return text_splitter.split_documents(documents)

    def ingest(self):
        texts = self._get_texts()
        self.index = VectorStoreIndexWrapper(
            vectorstore=Chroma.from_documents(
                texts,
                OpenAIEmbeddings(),
            )
        )

    def query_with_sources(self, query: str) -> QueryResult:
        return QueryResult(**self.index.query_with_sources(query))


class RepositoryIndexPersisted(RepositoryIndex):
    def __init__(self, path: str):
        super().__init__(path)
        self.persist_path = self.get_persist_path()

    def get_persist_path(self) -> str:
        hashed_path = hashlib.sha256(str(self.path).encode("utf-8")).hexdigest()
        short_hash = hashed_path[:8]
        base_name = os.path.basename(self.path)
        return os.path.join(BASE_PERSIST_PATH, f"{base_name}_{short_hash}")

    def ingest(self):
        pathlib.Path(self.persist_path).mkdir(parents=True, exist_ok=True)

        texts = self._get_texts()
        self.index = VectorStoreIndexWrapper(
            vectorstore=Chroma.from_documents(
                texts,
                OpenAIEmbeddings(),
                persist_directory=self.persist_path,
            )
        )

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
