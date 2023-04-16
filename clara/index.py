import os
import pathlib
import hashlib
import shutil
from typing import List
import glob

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import BaseRetriever

from .consts import (
    WILDCARDS,
    BASE_PERSIST_PATH,
)
from .config import config
from .console import console


class RepositoryIndex:
    def __init__(self, path: str, in_memory: bool = False):
        self.path = os.path.abspath(path)
        self.index = None
        self.in_memory = in_memory
        self.persist_path = self.get_persist_path()

    def get_persist_path(self) -> str:
        hashed_path = hashlib.sha256(str(self.path).encode("utf-8")).hexdigest()
        short_hash = hashed_path[:8]
        base_name = os.path.basename(self.path)
        return os.path.join(BASE_PERSIST_PATH, f"{base_name}_{short_hash}")

    def _get_texts(self):
        def get_files_by_wildcards(path: str, wildcards: List[str]) -> List[str]:
            matched_files = []

            for wc in wildcards:
                pattern = os.path.join(path, "**", wc)
                matched_files.extend(glob.glob(pattern, recursive=True))

            return matched_files

        if not os.path.exists(self.path):
            raise Exception(f"Path does not exists: {self.path}")

        documents = []
        for file_path in get_files_by_wildcards(self.path, WILDCARDS):
            console.log(f"Loading [blue underline]{file_path}", "…")
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load_and_split())

        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=100
        )
        return text_splitter.split_documents(documents)

    def ingest(self):
        if not self.in_memory:
            if os.path.exists(self.persist_path):
                vectorstore = Chroma(
                    persist_directory=self.persist_path,
                    embedding_function=OpenAIEmbeddings(),
                )
                self.index = VectorStoreIndexWrapper(vectorstore=vectorstore)
                return

            pathlib.Path(self.persist_path).mkdir(parents=True, exist_ok=True)

        texts = self._get_texts()
        self.index = VectorStoreIndexWrapper(
            vectorstore=Chroma.from_documents(
                texts,
                OpenAIEmbeddings(),
                persist_directory=self.persist_path if not self.in_memory else None,
            )
        )

    def persist(self):
        if not self.in_memory:
            self.index.vectorstore.persist()

    def clean(self):
        if not self.in_memory:
            shutil.rmtree(self.persist_path)

    def get_retriever(self) -> BaseRetriever:
        return self.index.vectorstore.as_retriever(
                search_type=config["index"]["search_type"],
                search_kwargs={"k": config["index"]["k"]},
            )
