import logging
import shutil

import fire
from rich.prompt import Confirm

from .console import console
from .index import RepositoryIndex, RepositoryIndexPersisted


# Disable ChromaDB logging
logger = logging.getLogger("chromadb").setLevel(logging.ERROR)


class Clara:
    """CLARA: Code Language Assistant & Repository Analyzer"""

    def config(self, path: str = "."):
        """Show config for a given path."""
        index = RepositoryIndexPersisted(path)
        console.print(f"Vector DB persist path = [blue underline]{index.persist_path}")

    def clean(self, path: str = "."):
        """Delete vector DB for a given path."""
        index = RepositoryIndexPersisted(path)
        if Confirm.ask(
            "Are you sure you want to remove "
            f"[blue underline]{index.persist_path}[/blue underline]?",
            default=False,
        ):
            shutil.rmtree(index.persist_path)

    def chat(self, path: str = ".", memory_storage: bool = False):
        """Chat about the code."""

        if memory_storage:
            index = RepositoryIndex(path)

        else:
            index = RepositoryIndexPersisted(path)

        if memory_storage or not index.load():
            with console.status(
                f"Ingesting code repository from path: [blue underline]{path} …",
                spinner="weather",
            ):
                index.ingest()

            if not memory_storage:
                with console.status(
                    "Storing vector database in path: "
                    "[blue underline]{index.persist_path} …",
                    spinner="weather",
                ):
                    index.persist()

        console.rule("[bold blue]CHAT")
        console.print("Hi, I'm Clara!", ":scroll::mag::robot:")
        console.print("How can I help you?")
        console.print()

        try:
            while True:
                query = console.input(">>> ")
                if not query:
                    continue

                with console.status("Querying…", spinner="weather"):
                    result = index.query_with_sources(query)

                console.print(
                    f"""
{result.answer.strip()}

[yellow]SOURCES[/yellow]

{result.sources}
"""
                )
                console.rule()
        except (KeyboardInterrupt, EOFError):
            console.print()
        finally:
            console.rule("[bold blue]END")
            console.print()
            console.print("Bye!", ":wave:")


def main():
    fire.Fire(Clara())
