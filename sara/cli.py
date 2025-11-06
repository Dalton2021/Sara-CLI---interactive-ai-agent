"""Sara CLI - AI Terminal Agent"""
import sys
import os
from pathlib import Path
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner

from .llm_client import LMStudioClient
from .vscode_context import VSCodeContext
from .file_context import FileContext


console = Console()


def build_system_prompt() -> str:
    """Build Sara's system prompt - she behaves like Claude Code"""
    return """You are Sara, an AI coding assistant. You are helpful, knowledgeable, and friendly.

Your role is to:
- Read and analyze code
- Suggest improvements and corrections
- Answer coding questions
- Help debug issues
- Explain code concepts
- Provide best practices

You have been given context about the user's current workspace and files. Use this context to provide relevant, specific assistance.

Be concise but thorough. Format your responses in markdown when appropriate. If you're suggesting code changes, show the specific lines that need modification."""


def gather_context(query: str, specific_file: str = None) -> str:
    """Gather context from VS Code and file system"""
    context_parts = []

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

    # Try to get open files from VS Code
    open_files = VSCodeContext.get_open_files()

    if open_files:
        context_parts.append("\n## Currently Open Files in VS Code:\n")
        for file_path in open_files[:3]:  # Limit to 3 files
            if os.path.exists(file_path):
                content = VSCodeContext.read_file_content(file_path, max_lines=200)
                context_parts.append(f"\n### {file_path}\n```\n{content}\n```\n")
    else:
        # Fallback: Get directory structure and relevant files
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

    return ''.join(context_parts)


@click.command()
@click.argument('query', nargs=-1, required=False)
@click.option('--file', '-f', help='Specific file to analyze')
@click.option('--no-context', is_flag=True, help='Skip gathering context')
@click.option('--interactive', '-i', is_flag=True, help='Start interactive mode')
def main(query, file, no_context, interactive):
    """Sara - AI Terminal Agent for Code Assistance

    Examples:
        sara "What does this code do?"
        sara "How can I optimize this function?" --file script.py
        sara --interactive
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

    # Interactive mode
    if interactive:
        console.print(Panel(
            "[cyan]Sara Interactive Mode[/cyan]\n\n"
            "Type your questions and I'll help you with coding tasks.\n"
            "Type 'exit' or 'quit' to leave.",
            title="Welcome",
            border_style="cyan"
        ))

        conversation_history = []
        while True:
            try:
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ")
                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("\n[cyan]Goodbye! Happy coding! 👋[/cyan]")
                    break

                if not user_input.strip():
                    continue

                # Gather context only for first message or on request
                context = ""
                if len(conversation_history) == 0:
                    console.print("[dim]Gathering context...[/dim]")
                    context = gather_context(user_input, file)

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
        if not no_context:
            with console.status("[cyan]Gathering context...[/cyan]", spinner="dots"):
                context = gather_context(query_text, file)

        # Build messages
        messages = [
            {"role": "system", "content": build_system_prompt()}
        ]

        if context:
            messages.append({"role": "system", "content": f"Context:\n{context}"})

        messages.append({"role": "user", "content": query_text})

        # Stream response
        console.print("\n[bold green]Sara:[/bold green] ", end="")
        try:
            for chunk in client.stream_chat(messages):
                console.print(chunk, end="")
            console.print("\n")
        except KeyboardInterrupt:
            console.print("\n\n[dim]Interrupted[/dim]")
            sys.exit(0)


if __name__ == '__main__':
    main()
