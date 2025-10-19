"""CLI main entry point."""

import asyncio
import sys

import click

from cli.output import format_session_output
from config import get_available_models, get_ollama_config
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
    default="mistral:latest",
    help="Ollama model to use (default: mistral:latest)",
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
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    help="Save results to file (supports .txt or .json)",
)
def generate(input: str, model: str, max_turns: int | None, verbose: bool, output: str | None) -> None:
    """Generate a creative slogan for INPUT.
    
    INPUT: Product or service description (e.g., "eco-friendly water bottle")
    
    Examples:
    
        slogan-gen generate "eco-friendly water bottle"
        
        slogan-gen generate "AI coding assistant" --model mistral:latest
        
        slogan-gen generate "cloud platform" --max-turns 10 --verbose
    """
    # Validate input
    if not input.strip():
        click.echo("❌ Error: Input cannot be empty", err=True)
        sys.exit(1)
    
    try:
        # Validate model exists (optional but recommended)
        try:
            available_models = get_available_models(timeout=5)
            if model not in available_models:
                click.echo(
                    f"⚠️  Warning: Model '{model}' not found in available models.\n",
                    err=True,
                )
                click.echo(f"Available models: {', '.join(sorted(available_models))}\n", err=True)
                
                if not click.confirm("Continue anyway?", default=False):
                    click.echo("\n💡 To install the model, run: ollama pull " + model)
                    sys.exit(1)
        except (ConnectionError, RuntimeError):
            # If we can't fetch models, just warn and continue
            click.echo(f"⚠️  Warning: Could not verify model availability\n", err=True)
        
        # Run the slogan generation workflow
        click.echo(f"🚀 Generating slogan for: {input}")
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
        output_text = format_session_output(session, verbose=verbose)
        click.echo(output_text)
        
        # Save to file if requested
        if output:
            try:
                import json
                from pathlib import Path
                
                output_path = Path(output)
                
                # Determine format based on extension
                if output_path.suffix.lower() == ".json":
                    # Save as JSON
                    with open(output_path, "w") as f:
                        json.dump(session.model_dump(mode="json"), f, indent=2, default=str)
                    click.echo(f"\n💾 Session saved to {output_path} (JSON format)")
                else:
                    # Save as text (default)
                    with open(output_path, "w") as f:
                        f.write(output_text)
                    click.echo(f"\n💾 Results saved to {output_path}")
                    
            except Exception as e:
                click.echo(f"\n⚠️  Warning: Could not save to file: {e}", err=True)
        
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


@cli.command()
@click.option(
    "--refresh",
    "-r",
    is_flag=True,
    help="Force refresh the model list from Ollama",
)
def models(refresh: bool) -> None:
    """List available Ollama models.
    
    Queries the Ollama API to display all installed models.
    
    Examples:
    
        slogan-gen models
        
        slogan-gen models --refresh
    """
    try:
        config = get_ollama_config()
        
        if refresh:
            click.echo("🔄 Refreshing model list...\n")
        
        available_models = get_available_models()
        
        if not available_models:
            click.echo("⚠️  No models found.")
            click.echo("\n💡 To install a model, run: ollama pull <model-name>")
            click.echo("   Example: ollama pull llama3.2:latest")
            return
        
        click.echo(click.style("📦 Available Ollama Models:", bold=True, fg="cyan"))
        click.echo()
        
        for i, model in enumerate(sorted(available_models), 1):
            # Highlight the default model
            if model == config.model_name:
                click.echo(f"  {i}. {click.style(model, fg='green', bold=True)} (default)")
            else:
                click.echo(f"  {i}. {model}")
        
        click.echo(f"\n✓ Total: {len(available_models)} models")
        click.echo(f"\n💡 Use with: slogan-gen generate \"your input\" --model <model-name>")
        
    except ConnectionError as e:
        click.echo(f"❌ {e}", err=True)
        click.echo("\n💡 Make sure Ollama is running: ollama serve", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error fetching models: {e}", err=True)
        sys.exit(1)


@cli.group()
def config() -> None:
    """Manage configuration settings.
    
    View and modify slogan generation configuration.
    """
    pass


@config.command(name="show")
def config_show() -> None:
    """Display current configuration settings.
    
    Shows all configuration values including defaults and environment overrides.
    
    Example:
    
        slogan-gen config show
    """
    try:
        cfg = get_ollama_config()
        
        click.echo(click.style("\n⚙️  Current Configuration:", bold=True, fg="cyan"))
        click.echo("=" * 60)
        
        # Format each config value
        settings = [
            ("Ollama Base URL", cfg.base_url),
            ("Default Model", cfg.model_name),
            ("Temperature", f"{cfg.temperature} (range: 0.0-2.0)"),
            ("Max Tokens", f"{cfg.max_tokens} (range: 1-4096)"),
            ("Timeout", f"{cfg.timeout}s (range: 1-300)"),
            ("Max Turns", f"{cfg.max_turns} (range: 1-10)"),
        ]
        
        for label, value in settings:
            click.echo(f"{label:.<25} {click.style(str(value), fg='green')}")
        
        click.echo("=" * 60)
        click.echo("\n💡 To modify settings, set environment variables:")
        click.echo("   Example: export OLLAMA_MODEL_NAME=mistral:latest")
        click.echo("   Or create a .env file in your project directory")
        
    except Exception as e:
        click.echo(f"❌ Error loading configuration: {e}", err=True)
        sys.exit(1)


@config.command(name="set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value via environment variable.
    
    KEY: Configuration key (e.g., MODEL_NAME, MAX_TURNS)
    VALUE: New value to set
    
    Note: This sets environment variables for the current session.
    For persistent changes, add to your .env file or shell profile.
    
    Example:
    
        slogan-gen config set MODEL_NAME mistral:latest
        
        slogan-gen config set MAX_TURNS 7
    """
    import os
    
    # Map friendly names to environment variable names
    key_mapping = {
        "MODEL_NAME": "OLLAMA_MODEL_NAME",
        "MODEL": "OLLAMA_MODEL_NAME",
        "BASE_URL": "OLLAMA_BASE_URL",
        "URL": "OLLAMA_BASE_URL",
        "TEMPERATURE": "OLLAMA_TEMPERATURE",
        "TEMP": "OLLAMA_TEMPERATURE",
        "MAX_TOKENS": "OLLAMA_MAX_TOKENS",
        "TOKENS": "OLLAMA_MAX_TOKENS",
        "TIMEOUT": "OLLAMA_TIMEOUT",
        "MAX_TURNS": "OLLAMA_MAX_TURNS",
        "TURNS": "OLLAMA_MAX_TURNS",
    }
    
    # Normalize key
    key_upper = key.upper()
    env_key = key_mapping.get(key_upper, f"OLLAMA_{key_upper}")
    
    try:
        # Set environment variable
        os.environ[env_key] = value
        
        # Clear cache to reload config
        get_ollama_config.cache_clear()
        
        # Validate by loading config
        cfg = get_ollama_config()
        
        click.echo(f"✓ Set {click.style(env_key, fg='cyan')} = {click.style(value, fg='green')}")
        click.echo(f"\n💡 This change is temporary for the current session.")
        click.echo(f"   For persistent changes, add to your .env file:")
        click.echo(f"   echo '{env_key}={value}' >> .env")
        
    except Exception as e:
        click.echo(f"❌ Error setting configuration: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
