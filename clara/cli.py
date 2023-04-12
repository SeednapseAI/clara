import fire
import logging

from .console import console
from .index import RepositoryIndexPersisted


# Disable ChromaDB logging
logger = logging.getLogger("chromadb").setLevel(logging.ERROR)


class Clara:
    """CLARA: Code Language Assistant & Repository Analyzer"""

    def config(self, path: str = "."):
        """Get config for a given path"""
        index = RepositoryIndexPersisted(path)
        console.print(f"Vector DB persist path = [blue underline]{index.persist_path}")

    def chat(self, path: str = "."):
        """Chat about the code"""
        index = RepositoryIndexPersisted(path)

        if not index.load():
            with console.status(
                f"Ingesting code repository from path: [blue underline]{path} …",
                spinner="weather",
            ):
                index.ingest()

            with console.status(
                f"Storing vector database in path: [blue underline]{index.persist_path} …",
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
