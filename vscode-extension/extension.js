const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Path where Sara will read context from
const CONTEXT_FILE = path.join(os.homedir(), '.sara-context.json');

/**
 * Write current VS Code context to file for Sara to read
 */
function updateContext() {
    const activeEditor = vscode.window.activeTextEditor;
    const visibleEditors = vscode.window.visibleTextEditors;
    const workspaceFolders = vscode.workspace.workspaceFolders;

    const context = {
        timestamp: Date.now(),
        activeFile: activeEditor ? activeEditor.document.uri.fsPath : null,
        activeFileLanguage: activeEditor ? activeEditor.document.languageId : null,
        openFiles: visibleEditors.map(editor => ({
            path: editor.document.uri.fsPath,
            language: editor.document.languageId,
            isDirty: editor.document.isDirty
        })),
        workspaceRoot: workspaceFolders && workspaceFolders.length > 0
            ? workspaceFolders[0].uri.fsPath
            : null,
        // Get all tabs (even those not visible)
        allOpenFiles: vscode.window.tabGroups.all.flatMap(group =>
            group.tabs.map(tab => {
                if (tab.input && tab.input.uri) {
                    return tab.input.uri.fsPath;
                }
                return null;
            })
        ).filter(f => f !== null)
    };

    try {
        fs.writeFileSync(CONTEXT_FILE, JSON.stringify(context, null, 2));
    } catch (error) {
        console.error('Failed to write Sara context file:', error);
    }
}

/**
 * Launch Sara in the VS Code terminal
 */
function launchSara(query = null) {
    const terminal = vscode.window.createTerminal('Sara');
    terminal.show();

    if (query) {
        terminal.sendText(`sara "${query}"`);
    } else {
        terminal.sendText('sara --interactive');
    }
}

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Sara Context Provider is now active!');

    // Update context immediately
    updateContext();

    // Update context when active editor changes
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(() => {
            updateContext();
        })
    );

    // Update context when visible editors change
    context.subscriptions.push(
        vscode.window.onDidChangeVisibleTextEditors(() => {
            updateContext();
        })
    );

    // Update context when document is saved
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(() => {
            updateContext();
        })
    );

    // Update context when tabs change
    context.subscriptions.push(
        vscode.window.tabGroups.onDidChangeTabs(() => {
            updateContext();
        })
    );

    // Command: Ask Sara about current file
    context.subscriptions.push(
        vscode.commands.registerCommand('sara.askAboutFile', async () => {
            const activeEditor = vscode.window.activeTextEditor;

            if (!activeEditor) {
                vscode.window.showWarningMessage('No file is currently open');
                return;
            }

            const question = await vscode.window.showInputBox({
                prompt: 'What would you like to ask Sara about this file?',
                placeHolder: 'e.g., "What does this code do?" or "Find bugs in this file"'
            });

            if (question) {
                updateContext();
                launchSara(question);
            }
        })
    );

    // Command: Start interactive Sara session
    context.subscriptions.push(
        vscode.commands.registerCommand('sara.interactive', () => {
            updateContext();
            launchSara();
        })
    );

    // Periodically update context (every 5 seconds)
    setInterval(updateContext, 5000);

    console.log('Sara Context Provider registered all event handlers');
}

function deactivate() {
    // Clean up context file on deactivation
    try {
        if (fs.existsSync(CONTEXT_FILE)) {
            fs.unlinkSync(CONTEXT_FILE);
        }
    } catch (error) {
        console.error('Failed to clean up Sara context file:', error);
    }
}

module.exports = {
    activate,
    deactivate
};
