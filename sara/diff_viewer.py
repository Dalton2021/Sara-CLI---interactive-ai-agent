"""Interactive diff viewer with keyboard navigation"""
import sys
import tty
import termios
from typing import Optional
from rich.console import Console
from rich.panel import Panel

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
        # Read the file to get line numbers
        try:
            with open(change.file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception:
            file_content = ""

        # Find the position in the file
        if change.old_code in file_content:
            lines_before = file_content[:file_content.find(change.old_code)].count('\n')
            start_line = lines_before + 1
        else:
            start_line = 1

        # Count additions and removals
        old_lines = change.old_code.split('\n')
        new_lines = change.new_code.split('\n')

        additions = 0
        removals = 0

        import difflib
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                removals += i2 - i1
            elif tag == 'insert':
                additions += j2 - j1
            elif tag == 'replace':
                removals += i2 - i1
                additions += j2 - j1

        # Header
        self.console.print()
        self.console.print(f"[bold]⏺ Update({change.file_path})[/bold]")
        self.console.print(f"  ⎿  Updated {change.file_path} with {additions} addition{'s' if additions != 1 else ''} and {removals} removal{'s' if removals != 1 else ''}")

        # Show diff with line numbers
        self.console.print()

        current_old_line = start_line
        current_new_line = start_line

        # Generate diff
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Show context (unchanged lines)
                for i in range(i1, min(i1 + 2, i2)):  # Show up to 2 context lines
                    line = old_lines[i]
                    self.console.print(f"     {current_old_line:>6}    {line}")
                    current_old_line += 1
                    current_new_line += 1

                # Skip middle lines if there are many
                if i2 - i1 > 4:
                    current_old_line += (i2 - i1 - 3)
                    current_new_line += (i2 - i1 - 3)

                # Show last context lines
                for i in range(max(i2 - 1, i1), i2):
                    if i >= i1 + 2:  # Only if we didn't already show it
                        line = old_lines[i]
                        self.console.print(f"     {current_old_line:>6}    {line}")
                        current_old_line += 1
                        current_new_line += 1

            elif tag == 'delete':
                # Removed lines
                for i in range(i1, i2):
                    line = old_lines[i]
                    self.console.print(f"     {current_old_line:>6} [black on red]-[/black on red]  [black on red]{line}[/black on red]")
                    current_old_line += 1

            elif tag == 'insert':
                # Added lines
                for j in range(j1, j2):
                    line = new_lines[j]
                    self.console.print(f"     {current_new_line:>6} [black on green]+[/black on green]  [black on green]{line}[/black on green]")
                    current_new_line += 1

            elif tag == 'replace':
                # Replaced lines (show as delete + insert)
                for i in range(i1, i2):
                    line = old_lines[i]
                    self.console.print(f"     {current_old_line:>6} [black on red]-[/black on red]  [black on red]{line}[/black on red]")
                    current_old_line += 1
                for j in range(j1, j2):
                    line = new_lines[j]
                    self.console.print(f"     {current_new_line:>6} [black on green]+[/black on green]  [black on green]{line}[/black on green]")
                    current_new_line += 1

        self.console.print()

        # Interactive menu
        return self._show_menu()

    def _show_menu(self) -> str:
        """Show interactive menu with keyboard navigation"""
        options = [
            ("confirm", "Yes", "green"),
            ("confirm_all", "Yes, allow all edits during this session", "green"),
            ("adjust", "No, and tell Sara what to do differently", "yellow")
        ]

        selected = 0

        self.console.print("[dim]Use ↑/↓ arrows to navigate, Enter to select, or press 1/2/3[/dim]")
        self.console.print()

        # Get original terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            # Set terminal to cbreak mode
            tty.setcbreak(fd)

            # Initial render
            for i, (action, label, color) in enumerate(options):
                if i == selected:
                    self.console.print(f" [bold {color}]❯ {i+1}. {label}[/bold {color}]")
                else:
                    self.console.print(f"[dim]   {i+1}. {label}[/dim]")

            while True:
                # Read a character
                char = sys.stdin.read(1)

                if char == '\x1b':  # Escape sequence
                    next_chars = sys.stdin.read(2)
                    if next_chars == '[A':  # Up arrow
                        selected = (selected - 1) % len(options)
                    elif next_chars == '[B':  # Down arrow
                        selected = (selected + 1) % len(options)
                    else:
                        continue

                    # Clear and redraw menu
                    sys.stdout.write(f"\033[{len(options)}A")  # Move cursor up
                    for i, (action, label, color) in enumerate(options):
                        sys.stdout.write("\033[2K")  # Clear line
                        if i == selected:
                            sys.stdout.write(f"\033[1;3{self._color_code(color)}m ❯ {i+1}. {label}\033[0m\n")
                        else:
                            sys.stdout.write(f"\033[2m   {i+1}. {label}\033[0m\n")
                    sys.stdout.flush()

                elif char == '\r' or char == '\n':  # Enter
                    break
                elif char == '1':  # Shortcut for option 1
                    selected = 0
                    break
                elif char == '2':  # Shortcut for option 2
                    selected = 1
                    break
                elif char == '3':  # Shortcut for option 3
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
            self.console.print("[green bold]✓ Applying change[/green bold]")
        elif action == "confirm_all":
            self.console.print("[green bold]✓ Applying all changes[/green bold]")
        elif action == "adjust":
            self.console.print("[yellow bold]Requesting adjustments...[/yellow bold]")

        return action

    def _color_code(self, color: str) -> int:
        """Get ANSI color code"""
        colors = {'green': 2, 'red': 1, 'yellow': 3}
        return colors.get(color, 7)

    def show_simple_confirmation(self, message: str) -> bool:
        """Show a simple yes/no confirmation"""
        self.console.print(f"\n{message}")
        self.console.print("[dim](y/n)[/dim] ", end="")

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
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
