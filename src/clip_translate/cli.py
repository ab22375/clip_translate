"""Command-line interface for clip_translate."""

import asyncio
import time
import typer
from rich.console import Console
from rich.table import Table
from loguru import logger
import pyperclip as clipboard

from clip_translate.core import TranslationEngine, get_supported_languages
from clip_translate.config import Config

app = typer.Typer(name="clip_translate", help="clip_translate CLI")
console = Console()
config = Config()


def validate_languages(src_lang: str, target_lang: str, engine: str = "google") -> None:
    """Validate that the source and target languages are supported."""
    supported = get_supported_languages(engine)
    if src_lang not in supported.keys() and src_lang != 'auto':
        raise typer.BadParameter(
            f"Unsupported source language: {src_lang}. "
            f"Supported languages are: {', '.join(supported.keys())}"
        )
    if target_lang not in supported.keys():
        raise typer.BadParameter(
            f"Unsupported target language: {target_lang}. "
            f"Supported languages are: {', '.join(supported.keys())}"
        )


async def translate_loop(
    source: str, 
    target: str, 
    show_original: bool = False,
    romaji: bool = False,
    hiragana: bool = False,
    once: bool = False,
    engine: str = "google"
) -> None:
    """Main translation loop."""
    # Set engine in config if specified
    if engine != config.get_engine():
        config.set_engine(engine)
        config.save_config()
    
    translation_engine = TranslationEngine(config)
    previous_text = ""
    
    # Setup Japanese converter if needed
    if source == "ja" and (romaji or hiragana):
        translation_engine.setup_japanese_converter(romaji, hiragana)

    while True:
        text = clipboard.paste()
        if text != previous_text and text:
            # First detect the language
            try:
                detected_lang = await translation_engine.detect_language(text.strip())
                
                # Only translate if detected language matches source language
                if detected_lang != source and source != 'auto':
                    console.print(f"\n[yellow]Skipped:[/yellow] Detected language '{detected_lang}' doesn't match source '{source}'")
                    previous_text = text
                    if once:
                        break
                    await asyncio.sleep(0.5)
                    continue
                    
            except Exception as e:
                console.print(f"[red]Language detection failed:[/red] {e}")
                if once:
                    break
                await asyncio.sleep(0.5)
                continue
            
            # Translate text
            try:
                translated_text, original_text, cached = await translation_engine.translate_text(
                    text, source, target
                )
            except Exception as e:
                console.print(f"[red]Translation failed:[/red] {e}")
                if once:
                    break
                await asyncio.sleep(0.5)
                continue

            # Don't copy translation to clipboard in CLI mode - keep original text
            cache_status = "[yellow][cached][/yellow]" if cached else "[cyan][new][/cyan]"
            console.print(f"\n{cache_status}")
            
            # Show original text if requested
            if show_original:
                console.print("[dim]Original:[/dim]")
                console.print(f"[green]{original_text}[/green]")
                
                # Show Japanese reading if requested
                if source == "ja" and (romaji or hiragana):
                    reading = translation_engine.get_japanese_reading(
                        original_text, romaji=romaji, hiragana=hiragana
                    )
                    if reading:
                        reading_label = "Romaji" if romaji else "Hiragana"
                        console.print(f"[dim]{reading_label}:[/dim]")
                        for line in reading.split('\n'):
                            console.print(f"[magenta]{line}[/magenta]")
                
                console.print("[dim]Translation:[/dim]")
            
            console.print(f"[bold]{translated_text}[/bold]")
            console.print("-" * 50)
            previous_text = text  # Keep tracking original clipboard text
            
            # Exit if only translating once
            if once:
                break

        await asyncio.sleep(0.5)
        
        # Exit if only translating once and nothing to translate
        if once:
            break


@app.command()
def translate(
    source: str = typer.Option("es", "--source", "-s", help="Source language code"),
    target: str = typer.Option("en", "--target", "-t", help="Target language code"),
    show_original: bool = typer.Option(False, "--show-original", "-o", help="Show original text before translation"),
    romaji: bool = typer.Option(False, "--romaji", "-r", help="Show romaji reading for Japanese text"),
    hiragana: bool = typer.Option(False, "--hiragana", "-h", help="Show hiragana reading for Japanese text"),
    once: bool = typer.Option(False, "--once", help="Translate only once instead of continuously"),
    engine: str = typer.Option(None, "--engine", "-e", help="Translation engine (google, openai, deepl, claude)"),
) -> None:
    """Translate text from clipboard."""
    try:
        # Use configured engine if not specified
        if engine is None:
            engine = config.get_engine()
        
        validate_languages(source, target, engine)
        
        # Check for conflicting options
        if romaji and hiragana:
            console.print("[bold red]Error: Cannot use both --romaji and --hiragana options together[/bold red]")
            raise typer.Exit(1)
            
        if once:
            console.print(f"[bold green]Waiting for {source} text in clipboard[/bold green] ({source} → {target}) using {engine}")
        else:
            console.print(
                f"[bold green]Translation started[/bold green] "
                f"({source} → {target}) using {engine}. Press Ctrl+C to stop."
            )
        
        if show_original:
            console.print("[dim]Showing original text[/dim]")
        if source == "ja" and romaji:
            console.print("[dim]Showing romaji readings[/dim]")
        if source == "ja" and hiragana:
            console.print("[dim]Showing hiragana readings[/dim]")

        asyncio.run(translate_loop(source, target, show_original, romaji, hiragana, once, engine))
    except KeyboardInterrupt:
        console.print("\n[bold red]Translation stopped by user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Cannot translate text:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def languages(
    engine: str = typer.Option(None, "--engine", "-e", help="Show languages for specific engine")
) -> None:
    """List all supported language codes."""
    if engine is None:
        engine = config.get_engine()
    
    supported = get_supported_languages(engine)
    console.print(f"[bold cyan]Supported language codes for {engine}:[/bold cyan]")
    for code, name in sorted(supported.items()):
        console.print(f"  {code:5s} - {name}")
    logger.info(f"Listed supported languages for {engine}")


@app.command()
def configure(
    engine: str = typer.Argument(None, help="Translation engine to configure"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="API key for the engine"),
    set_default: bool = typer.Option(False, "--set-default", "-d", help="Set as default engine")
) -> None:
    """Configure translation engines."""
    if engine is None:
        # Show current configuration
        table = Table(title="Translation Engine Configuration")
        table.add_column("Engine", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Default", style="yellow")
        
        current_engine = config.get_engine()
        engines = ["google", "openai", "deepl", "claude"]
        
        for eng in engines:
            if config.validate_engine_config(eng):
                status = "✓ Configured"
            else:
                status = "✗ Not configured"
            
            is_default = "Yes" if eng == current_engine else "No"
            table.add_row(eng, status, is_default)
        
        console.print(table)
        console.print(f"\nConfig file: {config.config_path}")
        return
    
    # Validate engine name
    if engine not in ["google", "openai", "deepl", "claude"]:
        console.print(f"[red]Unknown engine: {engine}[/red]")
        console.print("Available engines: google, openai, deepl, claude")
        raise typer.Exit(1)
    
    # Set API key if provided
    if api_key:
        config.set_api_key(engine, api_key)
        config.save_config()
        console.print(f"[green]API key set for {engine}[/green]")
    
    # Set as default if requested
    if set_default:
        config.set_engine(engine)
        config.save_config()
        console.print(f"[green]{engine} set as default engine[/green]")
    
    # Test configuration
    if config.validate_engine_config(engine):
        console.print(f"[green]{engine} is properly configured[/green]")
    else:
        if engine != "google":
            console.print(f"[yellow]{engine} needs API key configuration[/yellow]")
            console.print(f"Run: clip_translate configure {engine} --api-key YOUR_KEY")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()