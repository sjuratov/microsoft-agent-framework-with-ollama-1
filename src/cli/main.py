"""CLI main entry point."""

import asyncio
import sys

import click

from cli.output import format_session_output
from orchestration import run_slogan_generation


@click.group()
@click.version_option(version="0.1.0", prog_name="slogan-gen")
def cli() -> None:
    """AI-powered slogan generation using Writer-Reviewer collaboration."""
    pass


@cli.command()
@click.argument("input", required=True)
@click.option(
    "--model",
    default="llama3.2:latest",
    help="Ollama model to use (default: llama3.2:latest)",
)
@click.option(
    "--max-turns",
    type=click.IntRange(1, 10),
    default=None,
    help="Maximum iteration turns (default: 5, range: 1-10)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed iteration history",
)
def generate(input: str, model: str, max_turns: int | None, verbose: bool) -> None:
    """Generate a creative slogan for INPUT.
    
    INPUT: Product or service description (e.g., "eco-friendly water bottle")
    
    Examples:
    
        slogan-gen generate "eco-friendly water bottle"
        
        slogan-gen generate "AI coding assistant" --model llama3.2:latest
        
        slogan-gen generate "cloud platform" --max-turns 10 --verbose
    """
    # Validate input
    if not input.strip():
        click.echo("❌ Error: Input cannot be empty", err=True)
        sys.exit(1)
    
    try:
        # Run the slogan generation workflow
        click.echo(f"\n🚀 Generating slogan for: {input}")
        click.echo(f"   Using model: {model}")
        if max_turns:
            click.echo(f"   Max iterations: {max_turns}")
        click.echo()
        
        # Execute async workflow
        session = asyncio.run(
            run_slogan_generation(
                user_input=input,
                model_name=model,
                max_turns=max_turns,
            )
        )
        
        # Display results
        output = format_session_output(session, verbose=verbose)
        click.echo(output)
        
    except ValueError as e:
        click.echo(f"❌ Validation Error: {e}", err=True)
        sys.exit(1)
    except ConnectionError as e:
        click.echo(
            f"❌ Connection Error: {e}\n\n"
            f"💡 Tips:\n"
            f"   • Ensure Ollama is running: ollama serve\n"
            f"   • Check if the model is available: ollama list\n"
            f"   • Pull the model if needed: ollama pull {model}",
            err=True,
        )
        sys.exit(1)
    except RuntimeError as e:
        click.echo(f"❌ Workflow Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli()
