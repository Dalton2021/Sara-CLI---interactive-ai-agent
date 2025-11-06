# Sara - AI Terminal Agent

Sara is your AI coding assistant in the terminal. She can read files, suggest corrections, answer coding questions, and help with various development tasks. Sara uses the qwen3-coder-30b model hosted via LM Studio.

## Features

- ✏️ **Code Editing**: Sara can make changes to your code with interactive confirmation (just like Claude Code!)
- 🔍 **Context-Aware**: With the VS Code extension, Sara sees exactly which files you have open
- 💬 **Interactive Mode**: Have conversations with Sara about your code
- ⚡ **Streaming Responses**: Fast, real-time responses from your local LM Studio instance
- 📁 **File Analysis**: Analyze specific files or entire repositories
- 🎯 **Smart Context**: Intelligently gathers relevant files based on your query
- 🎨 **VS Code Integration**: Commands and shortcuts to invoke Sara directly from your editor
- 🔄 **Interactive Diffs**: Preview changes before applying, with keyboard navigation

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

## VS Code Extension (Recommended!)

For the best experience, install the Sara VS Code extension. This gives Sara the same context awareness as Claude Code - she'll know which files you have open!

```bash
# From the Sara directory
cp -r vscode-extension ~/.vscode/extensions/sara-context-provider
```

Then reload VS Code (`Cmd+Shift+P` → "Developer: Reload Window").

**See [INSTALL_EXTENSION.md](INSTALL_EXTENSION.md) for detailed instructions.**

With the extension installed, Sara automatically sees:
- ✅ Your currently active file
- ✅ All open tabs
- ✅ Workspace structure
- ✅ Updates in real-time

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

## Code Editing (NEW!)

Sara can now make changes to your code files with interactive confirmation! When she suggests changes, you'll see a diff and can choose:

- ✓ **Apply this change** - Sara modifies the file
- ✗ **Skip this change** - Leave the file unchanged
- ✎ **Deny and request adjustments** - Provide feedback and Sara will revise

### Example

```bash
sara "fix the bug in this file"
```

Sara will:
1. Analyze the code and identify the issue
2. Show you a diff of the proposed fix
3. Wait for your confirmation
4. Apply the change when you approve

**See [CODE_CHANGES.md](CODE_CHANGES.md) for detailed documentation.**

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
