#!/usr/bin/env python3
"""
Sara - A terminal-based AI assistant powered by gpt-oss-20b
"""

import os
import sys
import json
import asyncio
from typing import Optional, List, Dict
import argparse
from pathlib import Path

try:
    import openai
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.styles import Style
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
except ImportError:
    print("Error: Required packages not installed.")
    print("Please run: pip install openai prompt-toolkit rich")
    sys.exit(1)


class Sara:
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """Initialize Sara with API credentials"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

        if not self.api_key:
            raise ValueError("API key not found. Set OPENAI_API_KEY environment variable or pass it as an argument.")

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

        self.console = Console()
        self.conversation_history: List[Dict[str, str]] = []
        self.config_dir = Path.home() / ".sara"
        self.config_dir.mkdir(exist_ok=True)
        self.history_file = self.config_dir / "history"
        self.conversation_file = self.config_dir / "conversation.json"

        # Load previous conversation if exists
        self.load_conversation()

    def load_conversation(self):
        """Load the previous conversation history"""
        if self.conversation_file.exists():
            try:
                with open(self.conversation_file, 'r') as f:
                    self.conversation_history = json.load(f)
            except Exception as e:
                self.console.print(f"[yellow]Could not load conversation history: {e}[/yellow]")

    def save_conversation(self):
        """Save the current conversation history"""
        try:
            with open(self.conversation_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            self.console.print(f"[yellow]Could not save conversation: {e}[/yellow]")

    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
        if self.conversation_file.exists():
            self.conversation_file.unlink()
        self.console.print("[green]Conversation history cleared![/green]")

    async def chat(self, user_message: str, stream: bool = True) -> str:
        """Send a message and get a response"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            if stream:
                response_text = ""
                self.console.print("\n[bold cyan]Sara:[/bold cyan]", end=" ")

                stream_response = self.client.chat.completions.create(
                    model="gpt-oss-20b",
                    messages=self.conversation_history,
                    stream=True,
                    temperature=0.7,
                    max_tokens=4000
                )

                for chunk in stream_response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        response_text += content
                        print(content, end="", flush=True)

                print("\n")

            else:
                response = self.client.chat.completions.create(
                    model="gpt-oss-20b",
                    messages=self.conversation_history,
                    temperature=0.7,
                    max_tokens=4000
                )
                response_text = response.choices[0].message.content

                # Display with rich markdown rendering
                self.console.print("\n[bold cyan]Sara:[/bold cyan]")
                self.console.print(Markdown(response_text))
                print()

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            # Save conversation
            self.save_conversation()

            return response_text

        except Exception as e:
            self.console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n")
            # Remove the user message since we didn't get a response
            self.conversation_history.pop()
            return ""

    def run_interactive(self):
        """Run Sara in interactive mode"""
        # Custom style for the prompt
        style = Style.from_dict({
            'prompt': '#00aa00 bold',
        })

        # Create a prompt session with history
        session = PromptSession(
            history=FileHistory(str(self.history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            style=style
        )

        # Welcome message
        self.console.print(Panel.fit(
            "[bold cyan]Sara AI Assistant[/bold cyan]\n"
            "Powered by gpt-oss-20b\n\n"
            "Commands:\n"
            "  /clear  - Clear conversation history\n"
            "  /exit   - Exit Sara\n"
            "  /help   - Show this help message",
            border_style="cyan"
        ))
        print()

        # Main loop
        while True:
            try:
                # Get user input
                user_input = session.prompt([
                    ('class:prompt', 'You: ')
                ])

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.strip().startswith('/'):
                    command = user_input.strip().lower()

                    if command == '/exit' or command == '/quit':
                        self.console.print("\n[cyan]Goodbye! 👋[/cyan]\n")
                        break

                    elif command == '/clear':
                        self.clear_conversation()
                        continue

                    elif command == '/help':
                        self.console.print(Panel.fit(
                            "Commands:\n"
                            "  /clear  - Clear conversation history\n"
                            "  /exit   - Exit Sara\n"
                            "  /help   - Show this help message",
                            border_style="cyan",
                            title="Help"
                        ))
                        continue

                    else:
                        self.console.print(f"[yellow]Unknown command: {command}[/yellow]")
                        continue

                # Process the message
                asyncio.run(self.chat(user_input, stream=True))

            except KeyboardInterrupt:
                self.console.print("\n\n[cyan]Goodbye! 👋[/cyan]\n")
                break
            except EOFError:
                self.console.print("\n\n[cyan]Goodbye! 👋[/cyan]\n")
                break


def main():
    """Main entry point for Sara CLI"""
    parser = argparse.ArgumentParser(
        description="Sara - A terminal-based AI assistant powered by gpt-oss-20b"
    )
    parser.add_argument(
        '--api-key',
        help='OpenAI API key (or set OPENAI_API_KEY env var)'
    )
    parser.add_argument(
        '--api-base',
        help='API base URL (or set OPENAI_API_BASE env var)'
    )
    parser.add_argument(
        '--message', '-m',
        help='Send a single message and exit'
    )
    parser.add_argument(
        '--no-stream',
        action='store_true',
        help='Disable streaming responses'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear conversation history and exit'
    )

    args = parser.parse_args()

    try:
        sara = Sara(api_key=args.api_key, api_base=args.api_base)

        if args.clear:
            sara.clear_conversation()
            return

        if args.message:
            # Single message mode
            asyncio.run(sara.chat(args.message, stream=not args.no_stream))
        else:
            # Interactive mode
            sara.run_interactive()

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()