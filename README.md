# Sara - AI Terminal Agent

Sara is your AI coding assistant in the terminal. She can read files, suggest corrections, answer coding questions, and help with various development tasks. Sara uses the qwen3-coder-30b model hosted via LM Studio.

## Features

- 🔍 **Context-Aware**: Automatically detects VS Code open files and workspace structure
- 💬 **Interactive Mode**: Have conversations with Sara about your code
- ⚡ **Streaming Responses**: Fast, real-time responses from your local LM Studio instance
- 📁 **File Analysis**: Analyze specific files or entire repositories
- 🎯 **Smart Context**: Intelligently gathers relevant files based on your query

## Prerequisites

- Python 3.8 or higher
- LM Studio running locally at `http://127.0.0.1:1234`
- qwen3-coder-30b model (or any other model) loaded in LM Studio

## Installation

1. Clone this repository or navigate to the Sara directory:
```bash
cd /Users/dalton/Documents/AI/Sara
```

2. Install Sara:
```bash
pip install -e .
```

This will install Sara and make it available as the `sara` command in your terminal.

## Usage

### One-Shot Questions
Ask Sara a quick question:
```bash
sara "What does this code do?"
sara "How can I improve this function?"
```

### Analyze a Specific File
```bash
sara "Review this file for bugs" --file script.py
sara "Explain what this file does" -f main.py
```

### Interactive Mode
Start a conversation with Sara:
```bash
sara --interactive
# or
sara -i
```

In interactive mode, you can have back-and-forth conversations. Type `exit` or `quit` to leave.

### Skip Context Gathering
If you want a faster response without context:
```bash
sara "What is a closure in JavaScript?" --no-context
```

## How It Works

Sara gathers context from:
1. **VS Code open files** - Detects files you currently have open
2. **Workspace structure** - Understands your project layout
3. **Relevant files** - Finds files related to your query
4. **Specific files** - Analyzes files you explicitly specify

This context is sent to your local LM Studio instance, where the qwen3-coder-30b model generates helpful responses.

## Examples

```bash
# General coding question
sara "What's the difference between let and const in JavaScript?"

# Code review
sara "Review this file for security issues" --file api/auth.py

# Debug help
sara "Why might this function be causing a memory leak?" -f components/DataGrid.tsx

# Interactive debugging session
sara -i
> I'm getting a TypeError in my React component
> Can you help me understand why?
```

## Configuration

Sara uses these defaults:
- LM Studio URL: `http://127.0.0.1:1234`
- Temperature: `0.7`
- Max context files: `3`
- Max file lines: `1000`

To modify these, edit the values in `sara/cli.py` and `sara/llm_client.py`.

## Troubleshooting

**"Cannot connect to LM Studio"**
- Ensure LM Studio is running
- Check that the server is started (green play button in LM Studio)
- Verify the URL is `http://127.0.0.1:1234`

**"No context gathered"**
- Sara will fall back to repository scanning if VS Code files aren't detected
- Make sure you're in a directory with code files

**Slow responses**
- Use `--no-context` for faster responses without file context
- Reduce max_files in the configuration

## Development

To modify Sara:
1. Edit files in the `sara/` directory
2. Test changes: `python -m sara.cli "test query"`
3. Reinstall: `pip install -e .`

## License

MIT
