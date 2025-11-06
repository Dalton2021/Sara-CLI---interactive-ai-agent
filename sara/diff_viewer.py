"""Interactive diff viewer with keyboard navigation"""
import sys
import tty
import termios
from typing import Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from .code_editor import CodeChange


class DiffViewer:
    """Interactive diff viewer for confirming code changes"""

    def __init__(self, console: Console):
        self.console = console

    def show_change(self, change: CodeChange) -> str:
        """Show a code change and get user decision

        Returns:
            'confirm' - apply the change
            'deny' - skip this change
            'adjust' - deny and ask for adjustments
        """
        self.console.print()

        # Get file extension for syntax highlighting
        file_ext = change.file_path.split('.')[-1] if '.' in change.file_path else 'txt'
        language_map = {
            'py': 'python', 'js': 'javascript', 'ts': 'typescript',
            'html': 'html', 'css': 'css', 'json': 'json',
            'java': 'java', 'cpp': 'cpp', 'c': 'c', 'go': 'go',
            'rs': 'rust', 'rb': 'ruby', 'php': 'php'
        }
        language = language_map.get(file_ext, 'text')

        # Create side-by-side display
        from rich.columns import Columns
        from rich.table import Table

        # Create table for side-by-side diff
        table = Table(title=f"Proposed Change to: {change.file_path}",
                     title_style="bold cyan",
                     show_header=True,
                     header_style="bold",
                     border_style="cyan",
                     expand=True)

        table.add_column("OLD", style="red", no_wrap=False, ratio=1)
        table.add_column("NEW", style="green", no_wrap=False, ratio=1)

        # Split into lines and show side by side
        old_lines = change.old_code.split('\n')
        new_lines = change.new_code.split('\n')

        # Pad the shorter one
        max_lines = max(len(old_lines), len(new_lines))
        old_lines += [''] * (max_lines - len(old_lines))
        new_lines += [''] * (max_lines - len(new_lines))

        # Add lines with highlighting for differences
        for old_line, new_line in zip(old_lines, new_lines):
            if old_line != new_line:
                # Lines are different - highlight them
                table.add_row(
                    f"[red]{old_line}[/red]" if old_line else "",
                    f"[green]{new_line}[/green]" if new_line else ""
                )
            else:
                # Lines are the same - show in dim
                table.add_row(
                    f"[dim]{old_line}[/dim]",
                    f"[dim]{new_line}[/dim]"
                )

        self.console.print(table)

        # Interactive menu
        return self._show_menu()

    def _show_menu(self) -> str:
        """Show interactive menu with keyboard navigation"""
        options = [
            ("confirm", "✓ Apply this change", "green"),
            ("deny", "✗ Skip this change", "red"),
            ("adjust", "✎ Deny and request adjustments", "yellow")
        ]

        selected = 0

        self.console.print()
        self.console.print("[dim]Use ↑/↓ arrows to navigate, Enter to select, or press c/d/a[/dim]")
        self.console.print()

        def render_menu():
            # Move cursor up to redraw menu
            for i, (action, label, color) in enumerate(options):
                if i == selected:
                    self.console.print(f"[bold {color}]→ {label}[/bold {color}]")
                else:
                    self.console.print(f"[dim]  {label}[/dim]")

        # Initial render
        render_menu()

        # Get original terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            # Set terminal to raw mode for reading single characters
            tty.setraw(fd)

            while True:
                # Read a character
                char = sys.stdin.read(1)

                # Move cursor up to redraw menu
                if char == '\x1b':  # Escape sequence
                    next_chars = sys.stdin.read(2)
                    if next_chars == '[A':  # Up arrow
                        selected = (selected - 1) % len(options)
                        # Clear previous menu
                        self.console.print(f"\033[{len(options)}A", end="")
                        render_menu()
                    elif next_chars == '[B':  # Down arrow
                        selected = (selected + 1) % len(options)
                        # Clear previous menu
                        self.console.print(f"\033[{len(options)}A", end="")
                        render_menu()
                elif char == '\r' or char == '\n':  # Enter
                    break
                elif char.lower() == 'c':  # Shortcut for confirm
                    selected = 0
                    break
                elif char.lower() == 'd':  # Shortcut for deny
                    selected = 1
                    break
                elif char.lower() == 'a':  # Shortcut for adjust
                    selected = 2
                    break
                elif char == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt()

        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        self.console.print()
        action = options[selected][0]

        if action == "confirm":
            self.console.print("[green bold]✓ Change accepted[/green bold]")
        elif action == "deny":
            self.console.print("[red bold]✗ Change skipped[/red bold]")
        elif action == "adjust":
            self.console.print("[yellow bold]✎ Requesting adjustments...[/yellow bold]")

        return action

    def show_simple_confirmation(self, message: str) -> bool:
        """Show a simple yes/no confirmation"""
        self.console.print(f"\n{message}")
        self.console.print("[dim](y/n)[/dim] ", end="")

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            while True:
                char = sys.stdin.read(1).lower()
                if char == 'y':
                    self.console.print("y")
                    return True
                elif char == 'n':
                    self.console.print("n")
                    return False
                elif char == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
