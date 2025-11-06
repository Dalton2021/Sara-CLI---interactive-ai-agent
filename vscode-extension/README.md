# Sara Context Provider - VS Code Extension

This extension enables Sara AI to see which files you have open in VS Code, just like Claude Code!

## Features

- **Automatic Context Tracking**: Sara knows which file you're currently viewing
- **All Open Tabs**: Sara can see all your open files, not just visible ones
- **Workspace Awareness**: Sara understands your workspace structure
- **Keyboard Shortcuts**: Quick commands to invoke Sara
- **Terminal Integration**: Launch Sara directly from VS Code

## Installation

### From Source (Development)

1. Copy the `vscode-extension` folder to your VS Code extensions directory:

   **macOS/Linux:**
   ```bash
   cp -r vscode-extension ~/.vscode/extensions/sara-context-provider
   ```

   **Windows:**
   ```powershell
   Copy-Item -Recurse vscode-extension $env:USERPROFILE\.vscode\extensions\sara-context-provider
   ```

2. Reload VS Code:
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Developer: Reload Window"
   - Press Enter

3. The extension will start automatically and begin tracking your open files!

## Usage

### Automatic Context

Once installed, Sara will automatically know:
- Which file you're currently viewing
- What files you have open
- Your workspace root directory

Just use Sara normally from the terminal:
```bash
sara "What does this code do?"
sara "Find bugs in this file"
sara --interactive
```

### Commands

Access these from the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`):

- **Sara: Ask About Current File** - Opens a dialog to ask Sara about your active file
- **Sara: Start Interactive Session** - Launches Sara in interactive mode

### Keyboard Shortcuts

- `Cmd+Shift+S` (Mac) / `Ctrl+Shift+S` (Windows/Linux) - Ask about current file

## How It Works

The extension writes context information to `~/.sara-context.json` which includes:
- Active file path
- All open file paths
- Workspace root
- Language IDs
- Timestamps

Sara reads this file when gathering context, giving her the same awareness that Claude Code has!

## Troubleshooting

**Sara isn't seeing my open files:**
- Check if the extension is running: Look for "Sara Context Provider" in the Extensions panel
- Verify the context file exists: `cat ~/.sara-context.json`
- Reload VS Code window

**Extension not appearing:**
- Make sure you copied it to the correct extensions folder
- Check that the folder name is `sara-context-provider`
- Look for errors: Help > Toggle Developer Tools > Console

## Development

To modify the extension:

1. Edit `extension.js`
2. Reload VS Code window to test changes
3. Check console for debug output

## Requirements

- VS Code 1.80.0 or higher
- Sara AI Terminal Agent installed

## License

MIT
