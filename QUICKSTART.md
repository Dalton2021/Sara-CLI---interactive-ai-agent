# Sara - Quick Start Guide

## Installation (3 steps)

1. **Install Sara:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   Or manually:
   ```bash
   pip install -e .
   ```

2. **Set your API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Start chatting:**
   ```bash
   sara
   ```

## Common Commands

### Start Sara
```bash
sara
```

### Single message
```bash
sara -m "your question here"
```

### Clear history
```bash
sara --clear
```

### Custom API endpoint
```bash
export OPENAI_API_BASE="https://your-endpoint.com/v1"
sara
```

## Inside Sara

- Type your message and press Enter
- Use `/clear` to reset conversation
- Use `/exit` to quit
- Press ↑/↓ for command history
- Press Ctrl+C to exit

## Example Session

```bash
$ sara

You: What's the difference between a list and a tuple in Python?

Sara: Lists and tuples are both sequence types in Python, but have key differences:

1. **Mutability**: Lists are mutable (can be changed), tuples are immutable
2. **Syntax**: Lists use square brackets [], tuples use parentheses ()
3. **Performance**: Tuples are slightly faster
4. **Use case**: Use tuples for fixed data, lists for changing data

Example:
```python
my_list = [1, 2, 3]
my_list[0] = 10  # ✓ Works

my_tuple = (1, 2, 3)
my_tuple[0] = 10  # ✗ Error!
```

You: /exit

Goodbye! 👋
```

## Troubleshooting

**Problem**: "API key not found"
**Solution**: `export OPENAI_API_KEY="your-key"`

**Problem**: Command not found
**Solution**: Reinstall with `pip install -e .`

**Problem**: Import error
**Solution**: `pip install -r requirements.txt`

## Tips

- 💡 Sara remembers your conversation across sessions
- 💡 Use `/clear` if context gets too long
- 💡 Responses support markdown formatting
- 💡 Set API key permanently in `~/.bashrc`

For more details, see README.md