"""Command-line interface for clip_translate."""

import asyncio
import time
import typer
from rich.console import Console
from loguru import logger
from googletrans import Translator, LANGUAGES
import pyperclip as clipboard

app = typer.Typer(name="clip_translate", help="clip_translate CLI")
console = Console()


def validate_languages(src_lang: str, target_lang: str) -> None:
    """Validate that the source and target languages are supported."""
    if src_lang not in LANGUAGES.keys():
        raise typer.BadParameter(
            f"Unsupported source language: {src_lang}. "
            f"Supported languages are: {', '.join(LANGUAGES.keys())}"
        )
    if target_lang not in LANGUAGES.keys():
        raise typer.BadParameter(
            f"Unsupported target language: {target_lang}. "
            f"Supported languages are: {', '.join(LANGUAGES.keys())}"
        )


async def translate_loop(
    source: str, 
    target: str, 
    show_original: bool = False,
    romaji: bool = False,
    hiragana: bool = False,
    once: bool = False
) -> None:
    """Main translation loop."""
    translator = Translator()
    previous_text = ""
    cache = {}
    
    # Import Japanese reading libraries if needed
    converter = None
    if source == "ja" and (romaji or hiragana):
        try:
            import pykakasi
            kks = pykakasi.kakasi()
            converter = kks.convert
        except ImportError:
            console.print("[yellow]Warning: pykakasi not installed. Install with: uv add pykakasi[/yellow]")
            converter = None

    while True:
        text = clipboard.paste()
        if text != previous_text and text:
            # First detect the language
            try:
                detection = await translator.detect(text.strip())
                detected_lang = detection.lang
                
                # Only translate if detected language matches source language
                if detected_lang != source:
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
            
            if text in cache:
                translated_text, original_text = cache[text]
                cached = True
            else:
                translated = await translator.translate(
                    text.strip(), src=source, dest=target
                )
                # Remove empty lines from translated text
                translated_lines = [line for line in translated.text.strip().split('\n') if line.strip()]
                translated_text = '\n'.join(translated_lines)
                
                # Remove empty lines from original text
                original_lines = [line for line in text.strip().split('\n') if line.strip()]
                original_text = '\n'.join(original_lines)
                
                cache[text] = (translated_text, original_text)
                cached = False

            clipboard.copy(translated_text)
            cache_status = "[yellow][cached][/yellow]" if cached else "[cyan][new][/cyan]"
            console.print(f"\n{cache_status}")
            
            # Show original text if requested
            if show_original:
                console.print("[dim]Original:[/dim]")
                console.print(f"[cyan]{original_text}[/cyan]")
                
                # Show Japanese readings if requested and source is Japanese
                if source == "ja" and converter:
                    # Process each line separately for better formatting
                    lines = original_text.split('\n')
                    reading_lines = []
                    
                    for line in lines:
                        if line.strip():
                            result = converter(line)
                            if romaji:
                                # Convert to romaji
                                romaji_parts = []
                                for item in result:
                                    # Only show romaji if there's actual Japanese text
                                    if item['orig'] != item['hepburn']:
                                        romaji_parts.append(item['hepburn'])
                                    else:
                                        romaji_parts.append(item['orig'])
                                reading_line = ' '.join(romaji_parts)
                            else:  # hiragana
                                # Convert to hiragana
                                hiragana_parts = []
                                has_japanese = False
                                for item in result:
                                    # Check if this is actual Japanese text
                                    if item['orig'] != item['hira']:
                                        has_japanese = True
                                        hiragana_parts.append(item['hira'])
                                    else:
                                        hiragana_parts.append(item['orig'])
                                reading_line = ''.join(hiragana_parts)
                                # Skip showing if no Japanese was found
                                if not has_japanese:
                                    continue
                            reading_lines.append(reading_line)
                    
                    if reading_lines:
                        reading_label = "Romaji" if romaji else "Hiragana"
                        console.print(f"[dim]{reading_label}:[/dim]")
                        for line in reading_lines:
                            console.print(f"[magenta]{line}[/magenta]")
                
                console.print("[dim]Translation:[/dim]")
            
            console.print(f"[bold]{translated_text}[/bold]")
            console.print("-" * 50)
            previous_text = translated_text
            
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
) -> None:
    """Translate text from clipboard."""
    try:
        validate_languages(source, target)
        
        # Check for conflicting options
        if romaji and hiragana:
            console.print("[bold red]Error: Cannot use both --romaji and --hiragana options together[/bold red]")
            raise typer.Exit(1)
            
        if once:
            console.print(f"[bold green]Waiting for {source} text in clipboard[/bold green] ({source} → {target})")
        else:
            console.print(
                f"[bold green]Translation started[/bold green] "
                f"({source} → {target}). Press Ctrl+C to stop."
            )
        
        if show_original:
            console.print("[dim]Showing original text[/dim]")
        if source == "ja" and romaji:
            console.print("[dim]Showing romaji readings[/dim]")
        if source == "ja" and hiragana:
            console.print("[dim]Showing hiragana readings[/dim]")

        asyncio.run(translate_loop(source, target, show_original, romaji, hiragana, once))
    except KeyboardInterrupt:
        console.print("\n[bold red]Translation stopped by user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Cannot translate text:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def languages() -> None:
    """List all supported language codes."""
    console.print("[bold cyan]Supported language codes:[/bold cyan]")
    for code, name in sorted(LANGUAGES.items()):
        console.print(f"  {code:5s} - {name}")
    logger.info("Listed supported languages")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
