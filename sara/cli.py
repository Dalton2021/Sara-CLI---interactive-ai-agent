"""Sara CLI - AI Terminal Agent"""
import sys
import os
from pathlib import Path
import click
import textwrap
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from .llm_client import LMStudioClient
from .vscode_context import VSCodeContext
from .file_context import FileContext
from .code_editor import CodeEditor, CodeChange
from .diff_viewer import DiffViewer


console = Console()

# Style for the prompt
prompt_style = Style.from_dict({
    'prompt': 'bold cyan',
})

def build_system_prompt() -> str:
    """Build Sara's system prompt - she behaves like Claude Code"""
    return textwrap.dedent('''\
    You are Sara, an AI coding assistant. You are helpful, knowledgeable, and friendly, a little sassy but you're a cool gal.

    Your role is to:
    - Read and analyze code
    - Suggest improvements and corrections
    - Answer coding questions
    - Help debug issues
    - Explain code concepts
    - Provide best practices
    - Make code changes directly to files

    You have been given context about the user's current workspace and files. Use this context to provide relevant, specific assistance.

    ## Making Code Changes

    When you want to make changes to a file, create a diff for the user to view.

    CRITICAL RULES FOR MAKING CHANGES:
    1. **BE SURGICAL** - Show ONLY the lines that need to change, plus 1-2 lines of context
    2. **NEVER replace entire files** - Only show the specific section that needs modification
    3. **Keep it minimal** - For a missing semicolon or tag, show just 2-3 lines, not 50+
    4. **Match exactly** - The OLD code must match what's in the file (check spacing/indentation)
    5. **Include context** - Add 1-2 lines before/after so the change location is unique
    6. **Multiple changes** - Show each change separately, don't combine distant changes

    Good Example (fixing missing closing tag):
    "I found it! Line 72 is missing a closing </p> tag"

    Bad Example (replacing entire file):
    OLD:
    ```html
    <!DOCTYPE html>
    <html>
    ... entire 100 line file ...
    </html>
    ```
    This is way too much! Be surgical.

    Another Good Example (Python function fix):
    "The function crashes on empty lists. Let me add a check."

    The user will be shown a side-by-side diff and can confirm, deny, or request adjustments, so we do not need to show them an OLD an NEW section in our response, let the diff be their visual difference.

    Be concise but thorough. Format your responses in markdown when appropriate.
    ''')


def gather_context(query: str, specific_file: str = None) -> tuple[str, bool]:
    """Gather context from VS Code and file system

    Returns:
        tuple: (context_string, has_vscode_context)
    """
    context_parts = []
    has_vscode = VSCodeContext.has_extension_running()

    # Get workspace root
    workspace_root = VSCodeContext.get_workspace_root()
    context_parts.append(f"Working Directory: {workspace_root}\n")

    # If a specific file is provided, read it
    if specific_file:
        if os.path.exists(specific_file):
            content = VSCodeContext.read_file_content(specific_file)
            context_parts.append(f"\n## File: {specific_file}\n```\n{content}\n```\n")
        else:
            context_parts.append(f"\nNote: Specified file '{specific_file}' not found.\n")

    # Try to get active file from VS Code (prioritize this!)
    active_file = VSCodeContext.get_active_file()
    if active_file and os.path.exists(active_file):
        content = VSCodeContext.read_file_content(active_file, max_lines=500)
        context_parts.append(f"\n## Active File in VS Code: {active_file}\n```\n{content}\n```\n")

    # Get other open files from VS Code
    open_files = VSCodeContext.get_open_files()

    # Filter out the active file from open files list
    if active_file and open_files:
        open_files = [f for f in open_files if f != active_file]

    if open_files:
        context_parts.append("\n## Other Open Files in VS Code:\n")
        for file_path in open_files[:3]:  # Limit to 3 additional files
            if os.path.exists(file_path):
                content = VSCodeContext.read_file_content(file_path, max_lines=200)
                relative_path = os.path.basename(file_path)
                context_parts.append(f"\n### {relative_path}\n```\n{content}\n```\n")

    # If no VS Code context, fall back to file scanning
    if not has_vscode:
        context_parts.append("\n## Repository Structure:\n")
        structure = FileContext.get_directory_structure(workspace_root, max_depth=2)
        context_parts.append(structure)

        # Get relevant files based on query
        relevant_files = FileContext.get_relevant_files(workspace_root, query, max_files=3)
        if relevant_files:
            context_parts.append("\n## Relevant Files:\n")
            for file_path, content in relevant_files:
                # Truncate content if too long
                if len(content) > 3000:
                    content = content[:3000] + "\n... (truncated)"
                context_parts.append(f"\n### {file_path}\n```\n{content}\n```\n")

    return ''.join(context_parts), has_vscode


def process_response_for_changes(response: str, active_file: str = None) -> tuple[str, list[CodeChange]]:
    """Process Sara's response and extract any code changes

    Returns:
        (clean_response, changes)
    """
    # Extract changes from response
    changes = CodeEditor.extract_changes(response, active_file)

    # For now, return the full response (we'll show it before the diff)
    return response, changes


def handle_code_changes(changes: list[CodeChange], conversation_history: list = None) -> tuple[bool, str]:
    """Handle code changes with interactive confirmation

    Returns:
        (all_applied, feedback) - feedback is None unless user wants adjustments
    """
    if not changes:
        return True, None

    diff_viewer = DiffViewer(console)
    applied_changes = []
    feedback_messages = []
    auto_confirm = False  # Track if user selected "confirm all"

    for i, change in enumerate(changes):
        console.print(f"\n[cyan bold]Change {i+1} of {len(changes)}[/cyan bold]")

        # Validate the change
        is_valid, error_msg = CodeEditor.validate_change(change)
        if not is_valid:
            console.print(f"[red]✗ Cannot apply change: {error_msg}[/red]")
            console.print("[yellow]Tip: Ask Sara to show less code (just the lines that need to change)[/yellow]")
            feedback_messages.append(
                f"The change to {change.file_path} failed: {error_msg}. "
                "Please provide a smaller, more surgical change with just the exact lines from the file."
            )
            continue

        # Show the change and get user decision (unless auto-confirming)
        if auto_confirm:
            decision = "confirm"
            console.print(f"[green]✓ Auto-applying change to {change.file_path}[/green]")
        else:
            decision = diff_viewer.show_change(change)

        if decision == "confirm":
            # Apply the change
            if change.apply():
                applied_changes.append(change)
                console.print(f"[green]✓ Successfully applied change to {change.file_path}[/green]")
            else:
                console.print(f"[red]✗ Failed to apply change to {change.file_path}[/red]")

        elif decision == "confirm_all":
            # Apply this change and all remaining changes
            auto_confirm = True
            if change.apply():
                applied_changes.append(change)
                console.print(f"[green]✓ Successfully applied change to {change.file_path}[/green]")
            else:
                console.print(f"[red]✗ Failed to apply change to {change.file_path}[/red]")

        elif decision == "adjust":
            # User wants adjustments
            console.print("\n[yellow]What adjustments would you like Sara to make?[/yellow]")
            # Use a simple prompt session for this one-off input
            feedback_session = PromptSession()
            feedback = feedback_session.prompt("Your feedback: ", style=prompt_style)
            feedback_messages.append(f"For the change to {change.file_path}: {feedback}")

    # If there's feedback (either from validation failures or user requests), return it
    if feedback_messages:
        all_feedback = "\n".join(feedback_messages)
        console.print(f"\n[yellow]⚠ {len(feedback_messages)} issue(s) need to be addressed[/yellow]")
        return False, all_feedback

    # If we applied some changes, notify
    if applied_changes:
        console.print(f"\n[green bold]✓ Applied {len(applied_changes)} change(s)[/green bold]")
    elif changes:
        # Had changes but none were applied
        console.print(f"\n[yellow]No changes were applied[/yellow]")

    return True, None


@click.command()
@click.argument('query', nargs=-1, required=False)
@click.option('--file', '-f', help='Specific file to analyze')
@click.option('--no-context', is_flag=True, help='Skip gathering context')
@click.option('--interactive', '-i', is_flag=True, help='Start interactive mode')
def main(query, file, no_context, interactive):
    """Sara - AI Terminal Agent for Code Assistance

    Examples:
        sara                    # Start interactive mode (default)
        sara "What does this code do?"
        sara "How can I optimize this function?" --file script.py
    """
    # Initialize LM Studio client
    client = LMStudioClient()

    # Check connection
    if not client.check_connection():
        console.print(Panel(
            "[red]Cannot connect to LM Studio[/red]\n\n"
            "Make sure LM Studio is running at http://127.0.0.1:1234\n"
            "and that you have a model loaded.",
            title="Connection Error",
            border_style="red"
        ))
        sys.exit(1)

    # Default to interactive mode if no query provided
    if not query and not interactive:
        interactive = True

    # Interactive mode
    if interactive:
        console.print(Panel(
            "[cyan]Sara Interactive Mode[/cyan]\n\n"
            "Type your questions and I'll help you with coding tasks.\n"
            "Type 'exit' or 'quit' to leave.",
            title="Welcome",
            border_style="cyan"
        ))

        # Create prompt session for line editing
        session = PromptSession()

        conversation_history = []
        while True:
            try:
                console.print()
                # Use prompt_toolkit for proper line editing
                user_input = session.prompt("You: ", style=prompt_style)

                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("\n[cyan]Goodbye! Happy coding! 👋[/cyan]")
                    break

                if not user_input.strip():
                    continue

                # Gather context only for first message or on request
                context = ""
                has_vscode = False
                if len(conversation_history) == 0:
                    console.print("[dim]Gathering context...[/dim]")
                    context, has_vscode = gather_context(user_input, file)
                    if not has_vscode:
                        console.print("[dim yellow]💡 Tip: Install the Sara VS Code extension for better context awareness![/dim yellow]")

                # Build messages
                messages = [{"role": "system", "content": build_system_prompt()}]
                if context:
                    messages.append({"role": "system", "content": f"Context:\n{context}"})

                messages.extend(conversation_history)
                messages.append({"role": "user", "content": user_input})

                # Stream response
                console.print("\n[bold green]Sara:[/bold green] ", end="")
                response_text = ""
                for chunk in client.stream_chat(messages):
                    console.print(chunk, end="")
                    response_text += chunk
                console.print()  # New line after response

                # Check for code changes
                active_file = VSCodeContext.get_active_file()
                clean_response, changes = process_response_for_changes(response_text, active_file)

                if changes:
                    # Handle code changes with interactive confirmation
                    all_applied, feedback = handle_code_changes(changes, conversation_history)

                    if feedback:
                        # User wants adjustments OR validation failed
                        # Add feedback to conversation and get Sara to try again
                        conversation_history.append({"role": "user", "content": user_input})
                        conversation_history.append({"role": "assistant", "content": response_text})
                        conversation_history.append({
                            "role": "user",
                            "content": (
                                f"{feedback}\n\n"
                                "Remember: Show ONLY the specific lines that need to change, "
                                "plus 1-2 lines of context. Copy the EXACT code from the file."
                            )
                        })

                        # Get Sara's adjusted response
                        console.print("\n[cyan]Sara is revising her changes...[/cyan]\n")
                        console.print("[bold green]Sara:[/bold green] ", end="")
                        adjusted_response = ""
                        for chunk in client.stream_chat([{"role": "system", "content": build_system_prompt()}] + conversation_history):
                            console.print(chunk, end="")
                            adjusted_response += chunk
                        console.print()

                        # Try to apply adjusted changes
                        _, adjusted_changes = process_response_for_changes(adjusted_response, active_file)
                        if adjusted_changes:
                            all_applied, more_feedback = handle_code_changes(adjusted_changes, conversation_history)
                            # If still having issues, give up after one retry to avoid loops
                            if more_feedback:
                                console.print("\n[yellow]Still having issues. You may need to make this change manually.[/yellow]")

                        conversation_history.append({"role": "assistant", "content": adjusted_response})
                        continue

                # Add to history
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": response_text})

            except KeyboardInterrupt:
                console.print("\n\n[cyan]Goodbye! Happy coding! 👋[/cyan]")
                break
            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]")

    # One-shot mode
    else:
        if not query:
            console.print("[red]Please provide a query or use --interactive mode[/red]")
            console.print("\nUsage: sara \"your question here\"")
            console.print("       sara --interactive")
            sys.exit(1)

        query_text = ' '.join(query)

        # Gather context
        context = ""
        has_vscode = False
        if not no_context:
            with console.status("[cyan]Gathering context...[/cyan]", spinner="dots"):
                context, has_vscode = gather_context(query_text, file)

            if not has_vscode:
                console.print("[dim yellow]💡 Tip: Install the Sara VS Code extension for better context awareness![/dim yellow]\n")

        # Build messages
        messages = [
            {"role": "system", "content": build_system_prompt()}
        ]

        if context:
            messages.append({"role": "system", "content": f"Context:\n{context}"})

        messages.append({"role": "user", "content": query_text})

        # Stream response
        console.print("\n[bold green]Sara:[/bold green] ", end="")
        response_text = ""
        try:
            for chunk in client.stream_chat(messages):
                console.print(chunk, end="")
                response_text += chunk
            console.print("\n")

            # Check for code changes
            active_file = VSCodeContext.get_active_file()
            clean_response, changes = process_response_for_changes(response_text, active_file)

            if changes:
                # Handle code changes with interactive confirmation
                all_applied, feedback = handle_code_changes(changes)

                if feedback:
                    # User wants adjustments OR validation failed
                    console.print("\n[cyan]Sara is revising her changes...[/cyan]\n")

                    messages.append({"role": "assistant", "content": response_text})
                    messages.append({
                        "role": "user",
                        "content": (
                            f"{feedback}\n\n"
                            "Remember: Show ONLY the specific lines that need to change, "
                            "plus 1-2 lines of context. Copy the EXACT code from the file."
                        )
                    })

                    # Get adjusted response
                    console.print("[bold green]Sara:[/bold green] ", end="")
                    adjusted_response = ""
                    for chunk in client.stream_chat(messages):
                        console.print(chunk, end="")
                        adjusted_response += chunk
                    console.print("\n")

                    # Try to apply adjusted changes
                    _, adjusted_changes = process_response_for_changes(adjusted_response, active_file)
                    if adjusted_changes:
                        all_applied, more_feedback = handle_code_changes(adjusted_changes)
                        if more_feedback:
                            console.print("\n[yellow]Still having issues. You may need to make this change manually.[/yellow]")

        except KeyboardInterrupt:
            console.print("\n\n[dim]Interrupted[/dim]")
            sys.exit(0)


if __name__ == '__main__':
    main()
