"""
Console Utilities Module

This module provides utilities for console interaction in the setup script generator.
"""

import os
from pathlib import Path
from typing import Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.live import Live
from prompt_toolkit import prompt

# Initialize console
console = Console()


class Confirm:
    """Utility class for confirmation prompts."""

    @staticmethod
    def ask(question):
        """Ask a yes/no question and return the answer.

        Args:
            question: The question to ask

        Returns:
            True if the answer is yes, False otherwise
        """
        response = prompt(f"{question} [y/n] ").lower().strip()
        return response.startswith("y")


def print_welcome_message():
    """Print the welcome message for the setup script generator and wait for user to press Enter."""
    console.print(
        Panel(
            "[bold]Automated environment configuration powered by Augment[/bold]\n\n"
            + "[yellow]Workflow:[/yellow]\n"
            + "[dim]1.[/dim] [cyan]Select Test Command[/cyan] → Identifies appropriate validation command for the project\n"
            + "[dim]2.[/dim] [cyan]Generate Setup Script[/cyan] → Creates setup script and validates it by running the test command\n\n"
            + "[italic green]Press Enter to start...[/italic green]",
            title="[bold blue]AI Setup Script Generator[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
    )
    # Wait for user to press Enter
    input()


def print_file_saved_message(file_path: Path):
    """Print a message indicating that a file was saved.

    Args:
        file_path: Path to the saved file
    """
    console.print(f"\n[bold green]Setup script saved to: {file_path}[/bold green]")
    console.print("You can now use this script to set up your project.")


def display_script(script_content: str, file_path: Optional[Path] = None):
    """Display a script with syntax highlighting.

    Args:
        script_content: The content of the script
        file_path: Optional path to the script file
    """
    title = f"Setup Script ({file_path})" if file_path else "Setup Script"
    syntax = Syntax(script_content, "bash", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title))


def create_live_output_display(title: str = "Output", height: int = 20):
    """Create a live output display with fixed height and syntax highlighting.

    Args:
        title: Title for the panel
        height: Height of the output panel in lines

    Returns:
        A tuple of (Live, function to update content)
    """

    # Create a renderable that will be updated
    class LogDisplay:
        def __init__(self):
            self.log_lines = []

        def __rich__(self):
            # Create a syntax object with the current log lines
            # Only show the last 'height' lines if we have more
            display_lines = (
                self.log_lines[-height:]
                if len(self.log_lines) > height
                else self.log_lines
            )
            text = "\n".join(display_lines)
            return Panel(
                Syntax(
                    text,
                    "bash",  # Using bash lexer which works well for logs with commands
                    theme="monokai",
                    line_numbers=False,
                    word_wrap=True,
                ),
                title=title,
                border_style="green",
            )

    log_display = LogDisplay()

    def update_content(lines: List[str]):
        """Update the display with new content.

        Args:
            lines: List of log lines to display
        """
        log_display.log_lines = lines

    # Create the live display with a higher refresh rate for smoother updates
    live = Live(log_display, refresh_per_second=10)

    return live, update_content


def get_script_path(default_path: str = "setup.sh") -> Path:
    """Get the path to save the script.

    Args:
        default_path: Default path for the script

    Returns:
        Path object for the script
    """
    script_path = prompt(
        f"Where would you like to save the setup script? [default: {default_path}]: "
    )

    if not script_path:
        script_path = default_path

    # Convert to absolute path if not already
    if not os.path.isabs(script_path):
        script_path = os.path.abspath(script_path)

    return Path(script_path)
