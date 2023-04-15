import os
import pathlib
import hashlib
import shutil
from typing import List, Tuple, Iterable, Optional
from dataclasses import dataclass
import glob

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

from .consts import (
    WILDCARDS,
    BASE_PERSIST_PATH,
    PROMPT_PREFIX,
)
from .chat import create_chat
from .console import console


@dataclass
class QueryResult:
    question: str
    answer: str
    sources: List[Document]


class ChatHistory:
    def __init__(
        self, prompt_prefix: Optional[Tuple[str, str]] = None, length_limit: int = 3500
    ):
        self.prompt_prefix = prompt_prefix
        self.history = [prompt_prefix] if prompt_prefix else []
        self.length_limit = length_limit

    def append(self, messages: Tuple[str, str]):
        def get_total_length(messages: Iterable[str]) -> int:
            return sum(len(message) for message in messages)

        total_length = sum([get_total_length(message) for message in messages])
        if self.prompt_prefix:
            total_length += get_total_length(self.prompt_prefix)

        keep_history = 1

        while True:
            if keep_history > len(self.history):
                break

            next_length = total_length + get_total_length(self.history[-keep_history])
            if next_length > self.length_limit:
                break

            keep_history += 1

        if self.prompt_prefix:
            new_history = [self.history[0]]
        else:
            new_history = []

        new_history += self.history[-keep_history:-1]
        new_history += [messages]

        self.history = new_history


class RepositoryIndex:
    def __init__(self, path: str, in_memory: bool = False):
        self.path = os.path.abspath(path)
        self.index = None
        self.in_memory = in_memory
        self.persist_path = self.get_persist_path()

        self.chat = None
        self.chat_history = ChatHistory(prompt_prefix=PROMPT_PREFIX)

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

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
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

    def init_chat(self):
        # model = self.get_model()
        # self.chat = ConversationalRetrievalChain.from_llm(
        #     model,
        #     retriever=self.index.vectorstore.as_retriever(),
        #     return_source_documents=True,
        #     condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        # )

        self.chat = create_chat(self.index.vectorstore.as_retriever())

    def query_with_sources(self, query: str) -> QueryResult:
        # return QueryResult(**self.index.query_with_sources(query))
        if self.chat is None:
            self.init_chat()
        response = self.chat(
            {"question": query, "chat_history": self.chat_history.history}
            # {"question": query, "chat_history": ""}
        )
        # console.log(response)
        self.chat_history.append((response["question"], response["answer"]))
        return QueryResult(
            question=response["question"],
            answer=response["answer"],
            sources=response["source_documents"],
        )
