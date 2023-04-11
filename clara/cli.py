import fire

from .console import console
from .index import RepositoryIndex


class Clara:
    def chat(self, path: str = "."):
        index = RepositoryIndex(path)
        index.ingest()
        console.rule("[bold blue]CHAT")

        console.print("Hi, I'm Clara!", ":scroll::mag::robot:")
        console.print("How can I help you?")
        console.print()

        try:
            while True:
                query = console.input(">>> ")
                if not query:
                    continue
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
