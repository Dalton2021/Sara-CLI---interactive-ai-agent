# Sara - Terminal AI Assistant

A terminal-based AI assistant powered by gpt-oss-20b, inspired by Claude Code. Sara provides an interactive chat interface directly in your terminal with conversation history, streaming responses, and beautiful formatting.

## Features

- 🚀 **Interactive Chat Mode**: Continuous conversation with context memory
- 💬 **Streaming Responses**: See responses appear in real-time
- 📝 **Conversation History**: Automatically saves and loads your chat history
- 🎨 **Rich Formatting**: Beautiful markdown rendering in the terminal
- 🔍 **Command History**: Navigate previous commands with arrow keys
- ⚡ **Single Message Mode**: Send one-off queries without entering interactive mode

## Installation

### Option 1: Install with pip (Recommended)

```bash
# Clone or download the repository
cd sara

# Install the package
pip install -e .

# Or install directly
pip install .
```

### Option 2: Install from requirements

```bash
pip install -r requirements.txt
chmod +x sara.py
# Create a symlink or alias to use 'sara' command
```

### Option 3: Run directly

```bash
pip install openai prompt-toolkit rich
python sara.py
```

## Configuration

Sara needs an API key to communicate with the gpt-oss-20b model. Set your API credentials:

```bash
# Set your API key
export OPENAI_API_KEY="your-api-key-here"

# If using a custom API endpoint (optional)
export OPENAI_API_BASE="https://your-custom-endpoint.com/v1"
```

For persistent configuration, add these to your `~/.bashrc`, `~/.zshrc`, or equivalent:

```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### Interactive Mode

Simply run `sara` to start an interactive session:

```bash
sara
```

You'll enter a chat interface where you can have ongoing conversations:

```
┌────────────────────────────────────────┐
│ Sara AI Assistant                      │
│ Powered by gpt-oss-20b                 │
│                                        │
│ Commands:                              │
│   /clear  - Clear conversation history │
│   /exit   - Exit Sara                  │
│   /help   - Show this help message     │
└────────────────────────────────────────┘

You: Hello! Can you help me with Python?
Sara: Of course! I'd be happy to help you with Python...
```

### Interactive Commands

While in interactive mode, you can use these commands:

- `/clear` - Clear the conversation history
- `/exit` or `/quit` - Exit Sara
- `/help` - Show help information
- `Ctrl+C` or `Ctrl+D` - Quick exit

### Single Message Mode

Send a single message and get a response without entering interactive mode:

```bash
sara -m "What is the capital of France?"
sara --message "Explain async/await in Python"
```

### Command Line Options

```bash
sara --help                           # Show help
sara --api-key YOUR_KEY              # Provide API key directly
sara --api-base https://custom.com   # Use custom API endpoint
sara -m "your message"               # Send single message
sara --no-stream                     # Disable streaming (show complete response)
sara --clear                         # Clear conversation history and exit
```

## Examples

### Example 1: Quick Question

```bash
$ sara -m "How do I reverse a list in Python?"
Sara: There are several ways to reverse a list in Python:

1. Using slicing: `reversed_list = my_list[::-1]`
2. Using reverse() method: `my_list.reverse()` (modifies in place)
3. Using reversed(): `reversed_list = list(reversed(my_list))`
```

### Example 2: Interactive Coding Help

```bash
$ sara

You: I need to parse a JSON file in Python. Can you show me how?

Sara: Here's how to parse a JSON file in Python:

```python
import json

# Reading from a file
with open('data.json', 'r') as file:
    data = json.load(file)
    print(data)
```

You: What if the JSON is invalid?

Sara: You should use try-except to handle potential errors:
...
```

### Example 3: Custom API Endpoint

```bash
# Use a different API endpoint
sara --api-base https://your-custom-endpoint.com/v1 --api-key your-key
```

## File Structure

```
sara/
├── sara.py              # Main application
├── setup.py             # Package installation configuration
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── ~/.sara/            # User data directory (created automatically)
    ├── history         # Command history
    └── conversation.json  # Saved conversation
```

## Configuration Directory

Sara stores data in `~/.sara/`:
- `history` - Command-line history for autocomplete
- `conversation.json` - Your conversation history (persists between sessions)

## Troubleshooting

### "API key not found" error
Make sure you've set the `OPENAI_API_KEY` environment variable:
```bash
export OPENAI_API_KEY="your-key"
```

### Import errors
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Permission denied
Make the script executable:
```bash
chmod +x sara.py
```

### Custom model
If you're using a different model name, modify the `model` parameter in `sara.py`:
```python
model="your-model-name"
```

## Customization

You can customize Sara by editing `sara.py`:

- **Model**: Change the model name (line ~89)
- **Temperature**: Adjust response creativity (line ~91)
- **Max tokens**: Change response length (line ~92)
- **Colors**: Modify the Rich console styling
- **System prompt**: Add a system message to the conversation history

## Tips

1. **Context Awareness**: Sara remembers your conversation within a session and across sessions
2. **Clear when needed**: Use `/clear` to start fresh if the context gets too long
3. **Arrow keys**: Use ↑ and ↓ to navigate through your command history
4. **Tab completion**: The prompt-toolkit provides helpful autosuggestions
5. **Markdown**: Sara's responses support markdown formatting for better readability

## Requirements

- Python 3.8 or higher
- OpenAI-compatible API endpoint with gpt-oss-20b access
- Terminal with ANSI color support (most modern terminals)

## License

MIT License - feel free to modify and distribute as needed.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Comparison to Claude Code

While inspired by Claude Code, Sara is:
- Lighter weight and easier to customize
- Focused on general chat rather than coding workflows
- Compatible with any OpenAI-compatible API
- Simple to understand and modify

## Future Improvements

Potential enhancements:
- Multi-modal support (images, files)
- Tool/function calling
- Export conversations to various formats
- Multiple conversation threads
- Integration with local file system for context
- Plugin system for extensions

---

Made with ❤️ for terminal enthusiasts