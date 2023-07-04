import os
import pathlib
import hashlib
import shutil
from typing import List, Optional
from abc import ABC, abstractmethod
import glob
import ast

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import BaseRetriever
import tokenize

import esprima
import nbformat

from .consts import (
    WILDCARDS,
    BASE_PERSIST_PATH,
)
from .config import config
from .console import console


class LanguageParsing(ABC):
    def __init__(self, code: str):
        self.code = code

    def is_valid(self) -> bool:
        return True

    @abstractmethod
    def simplify_code(self):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def extract_functions_classes(self):
        raise NotImplementedError  # pragma: no cover


class PythonParsing(LanguageParsing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_lines = self.code.splitlines()

    def is_valid(self) -> bool:
        try:
            ast.parse(self.code)
            return True
        except SyntaxError:
            return False

    def _extract_code(self, node) -> str:
        start = node.lineno - 1
        end = node.end_lineno
        return "\n".join(self.source_lines[start:end])

    def extract_functions_classes(self) -> List[str]:
        tree = ast.parse(self.code)
        functions_classes = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                functions_classes.append(self._extract_code(node))

        return functions_classes

    def simplify_code(self) -> str:
        tree = ast.parse(self.code)
        simplified_lines = self.source_lines[:]

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                simplified_lines[start] = f"# Code for: {simplified_lines[start]}"

                for line_num in range(start + 1, node.end_lineno):
                    simplified_lines[line_num] = None

        return "\n".join(line for line in simplified_lines if line is not None)


class NotebookParsing(PythonParsing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _, self.notebook = nbformat.validator.normalize(
            nbformat.reads(self.code, as_version=4)
        )

    def extract_functions_classes(self) -> List[str]:
        return []

    def simplify_code(self) -> str:
        markdown_output = []

        for cell in self.notebook.cells:
            if cell.cell_type == "markdown":
                markdown_output.append(cell.source)
            elif cell.cell_type == "code":
                source_code = cell.source.strip()
                if source_code:  # only include code blocks with content
                    markdown_output.append(f"```python\n{source_code}\n```")
            elif cell.cell_type == "raw":
                markdown_output.append(cell.source)

        return "\n\n".join(markdown_output)


class JavascriptParsing(LanguageParsing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_lines = self.code.splitlines()

    def is_valid(self) -> bool:
        try:
            esprima.parseScript(self.code)
            return True
        except esprima.Error:
            return False

    def _extract_code(self, node) -> str:
        start = node.loc.start.line - 1
        end = node.loc.end.line
        return "\n".join(self.source_lines[start:end])

    def extract_functions_classes(self) -> List[str]:
        tree = esprima.parseScript(self.code, loc=True)
        functions_classes = []

        for node in tree.body:
            if isinstance(
                node,
                (esprima.nodes.FunctionDeclaration, esprima.nodes.ClassDeclaration),
            ):
                functions_classes.append(self._extract_code(node))

        return functions_classes

    def simplify_code(self) -> str:
        tree = esprima.parseScript(self.code, loc=True)
        simplified_lines = self.source_lines[:]

        for node in tree.body:
            if isinstance(
                node,
                (esprima.nodes.FunctionDeclaration, esprima.nodes.ClassDeclaration),
            ):
                start = node.loc.start.line - 1
                simplified_lines[start] = f"// Code for: {simplified_lines[start]}"

                for line_num in range(start + 1, node.loc.end.line):
                    simplified_lines[line_num] = None

        return "\n".join(line for line in simplified_lines if line is not None)


LANGUAGE_PARSERS = {
    "py": {
        "parser": PythonParsing,
        "language": "python",
        "type": "source_code",
    },
    "ipynb": {
        "parser": NotebookParsing,
        "language": "python",
        "type": "notebook",
    },
    "js": {
        "parser": JavascriptParsing,
        "language": "javascript",
        "type": "source",
    },
}


class CodeLoader(BaseLoader):
    """Load source code files."""

    def __init__(self, file_path: str, encoding: Optional[str] = None):
        """Initialize with file path."""
        if encoding is None:
            with open(file_path, "rb") as f:
                encoding, _ = tokenize.detect_encoding(f.readline)
        self.file_path = file_path
        self.encoding = encoding

    @staticmethod
    def get_extension(file_path: str) -> str:
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower().split(".", 1)[-1]

    @staticmethod
    def has_loader(file_path: str) -> bool:
        return CodeLoader.get_extension(file_path) in LANGUAGE_PARSERS

    def _get_extension(self) -> str:
        return CodeLoader.get_extension(self.file_path)

    def load(self) -> List[Document]:
        """Load from file path."""
        with open(self.file_path, encoding=self.encoding) as f:
            code = f.read()
        documents = []
        extension = self._get_extension()
        Parser = LANGUAGE_PARSERS[extension]["parser"]
        language = LANGUAGE_PARSERS[extension]["language"]
        file_type = LANGUAGE_PARSERS[extension]["type"]
        parser = Parser(code)
        if not parser.is_valid():
            return [Document(page_content=code, metadata={"source": self.file_path})]
        for functions_classes in parser.extract_functions_classes():
            documents.append(
                Document(
                    page_content=functions_classes,
                    metadata={
                        "source": self.file_path,
                        "file_type": file_type,
                        "content_type": "functions_classes",
                        "language": language,
                    },
                )
            )
        documents.append(
            Document(
                page_content=parser.simplify_code(),
                metadata={
                    "source": self.file_path,
                    "file_type": file_type,
                    "content_type": "simplified_code",
                    "language": language,
                },
            )
        )
        return documents


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
            # Skip if the path is a directory
            if not os.path.isfile(file_path):
                continue

            console.log(f"Loading [blue underline]{file_path}", "…")
            if CodeLoader.has_loader(file_path):
                loader = CodeLoader(file_path)
            else:
                loader = TextLoader(file_path)
            documents.extend(loader.load_and_split())

        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=config["index"]["chunk_size"],
            chunk_overlap=config["index"]["chunk_overlap"],
            disallowed_special=(),
        )
        return text_splitter.split_documents(documents)

    def ingest(self):
        if not self.in_memory:
            if os.path.exists(self.persist_path):
                vectorstore = Chroma(
                    persist_directory=self.persist_path,
                    embedding_function=OpenAIEmbeddings(disallowed_special=()),
                )
                self.index = VectorStoreIndexWrapper(vectorstore=vectorstore)
                return

            pathlib.Path(self.persist_path).mkdir(parents=True, exist_ok=True)

        texts = self._get_texts()
        self.index = VectorStoreIndexWrapper(
            vectorstore=Chroma.from_documents(
                texts,
                OpenAIEmbeddings(disallowed_special=()),
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
