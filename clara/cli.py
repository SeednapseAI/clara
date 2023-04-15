import os
import pathlib
import logging

import fire
from rich.prompt import Confirm
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
import click
from openai.error import InvalidRequestError

from .consts import HELP_MESSAGE
from .console import console
from .index import RepositoryIndex


# Disable warnings
# logging.getLogger().setLevel(logging.ERROR)


class Clara:
    """CLARA: Code Language Assistant & Repository Analyzer"""

    def config(self, path: str = "."):
        """Show config for a given path."""
        index = RepositoryIndex(path)
        console.print(f"Vector DB persist path = [blue underline]{index.persist_path}")

    def clean(self, path: str = "."):
        """Delete vector DB for a given path."""
        index = RepositoryIndex(path)
        if Confirm.ask(
            "Are you sure you want to remove "
            f"[blue underline]{index.persist_path}[/blue underline]?",
            default=False,
        ):
            index.clean()

    def chat(self, path: str = ".", memory_storage: bool = False):
        """Chat about the code."""

        index = RepositoryIndex(path, in_memory=memory_storage)

        with console.status(
            f"Ingesting code repository from path: [blue underline]{path} …",
            spinner="weather",
        ):
            index.ingest()

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

        last_sources = []

        pathlib.Path(index.persist_path).mkdir(parents=True, exist_ok=True)
        file_history_path = os.path.join(index.persist_path, "history.txt")
        session = PromptSession(history=FileHistory(file_history_path))

        try:
            while True:
                query = session.prompt(">>> ")
                query = query.strip()
                if not query:
                    continue

                if query.startswith("/"):
                    query = query.lower()

                    if query == "/context":
                        for source in last_sources:
                            console.print()
                            console.print(source.page_content)
                            console.print(
                                f"- [blue underline]{source.metadata['source']}"
                            )
                        continue
                    elif query in ("/exit", "/quit"):
                        break
                    elif query == "/edit":
                        query = click.edit()
                        query = query.strip()
                        session.history.append_string(query)
                        console.print(">>>", query)
                    elif query == "/help":
                        console.print(HELP_MESSAGE)
                        continue
                    else:
                        console.print(
                            ":no_entry: "
                            "[bold red]Unknown command."
                        )
                        continue

                try:
                    with console.status("Querying…", spinner="weather"):
                        result = index.query_with_sources(query)
                    console.print()
                    console.print(Markdown(result.answer))
                    console.print()
                    console.print("[yellow]SOURCES[/yellow]")
                    for source in result.sources:
                        console.print(f"- [blue underline]{source.metadata['source']}")
                    last_sources = result.sources
                # except InvalidRequestError:
                #     console.print(
                #         ":no_entry: "
                #         "[bold red]Ups, the request was invalid for some reason."
                #     )
                finally:
                    pass
                console.rule()
        except (KeyboardInterrupt, EOFError):
            console.print()
        finally:
            console.rule("[bold blue]END")
            console.print()
            console.print("Bye!", ":wave:")


def main():
    fire.Fire(Clara())
