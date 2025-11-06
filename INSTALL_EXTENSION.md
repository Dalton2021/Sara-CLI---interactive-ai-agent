# Installing the Sara VS Code Extension

The Sara VS Code Extension gives Sara the same context awareness that Claude Code has - she'll know which files you have open and can provide much more relevant assistance!

## Quick Install

Run this command from the Sara directory:

```bash
cp -r vscode-extension ~/.vscode/extensions/sara-context-provider
```

## After Installing

1. **Reload VS Code**:
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Developer: Reload Window"
   - Press Enter

2. **Verify It's Running**:
   - Open any code file
   - Run this command:
     ```bash
     cat ~/.sara-context.json
     ```
   - You should see JSON with your current file info!

3. **Test Sara**:
   - Open a code file in VS Code
   - In the VS Code terminal, run:
     ```bash
     sara "explain this file"
     ```
   - Sara will now see the file you have open!

## Using Sara with VS Code Context

### From Terminal
```bash
# Sara automatically sees your active file
sara "what does this code do?"

# Ask about your open files
sara "are there any bugs in these files?"

# Interactive mode with full context
sara --interactive
```

### From VS Code Command Palette
Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux) and type:
- **"Sara: Ask About Current File"** - Ask Sara about the file you're viewing
- **"Sara: Start Interactive Session"** - Launch Sara interactively

### Keyboard Shortcut
- `Cmd+Shift+S` (Mac) or `Ctrl+Shift+S` (Windows/Linux) - Quick ask about current file

## How It Works

The extension tracks:
- ✅ Active file (the one you're looking at)
- ✅ All open tabs (even if not visible)
- ✅ Workspace root
- ✅ File language types
- ✅ Updates in real-time (every 5 seconds)

All this info is written to `~/.sara-context.json` which Sara reads automatically.

## Troubleshooting

**Extension not working?**
```bash
# Check if extension is installed
ls -la ~/.vscode/extensions/sara-context-provider

# Check if context file is being created
cat ~/.sara-context.json

# Look for the timestamp - should be recent
cat ~/.sara-context.json | grep timestamp
```

**Sara not seeing context?**
- Make sure you've reloaded VS Code after installing the extension
- Check that the context file is less than 60 seconds old
- Try opening a code file and running `cat ~/.sara-context.json` again

**Still having issues?**
- Open VS Code Developer Tools: `Help > Toggle Developer Tools`
- Look for "Sara Context Provider" messages in the Console
- Check for any error messages

## Benefits

With the extension installed, Sara can:
- 🎯 **Focus on your active file** instead of scanning the whole repository
- 👀 **See what you're working on** without you specifying file paths
- 🚀 **Respond faster** with more relevant context
- 💡 **Understand your workflow** by seeing related open files

Enjoy your smarter Sara! 🤖
