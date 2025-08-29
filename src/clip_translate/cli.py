"""Command-line interface for clip_translate."""

import typer
from rich.console import Console
from loguru import logger

app = typer.Typer(name="clip_translate", help="clip_translate CLI")
console = Console()


@app.command()
def hello(name: str = typer.Option("World", help="Name to greet")) -> None:
    """Say hello to someone."""
    console.print(f"Hello, [bold cyan]{name}[/bold cyan]! 👋")
    logger.info(f"Greeted {name}")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
