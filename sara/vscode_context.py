"""VS Code integration to detect open files and workspace context"""
import os
import json
import time
from pathlib import Path
from typing import Optional


class VSCodeContext:
    CONTEXT_FILE = os.path.expanduser('~/.sara-context.json')
    CONTEXT_MAX_AGE = 60  # seconds

    @staticmethod
    def get_context() -> Optional[dict]:
        """Read context file written by VS Code extension"""
        try:
            if not os.path.exists(VSCodeContext.CONTEXT_FILE):
                return None

            # Check if file is recent (updated within last minute)
            mtime = os.path.getmtime(VSCodeContext.CONTEXT_FILE)
            if time.time() - mtime > VSCodeContext.CONTEXT_MAX_AGE:
                return None

            with open(VSCodeContext.CONTEXT_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError, FileNotFoundError):
            return None

    @staticmethod
    def get_active_file() -> Optional[str]:
        """Get the currently active file in VS Code"""
        context = VSCodeContext.get_context()
        if context and context.get('activeFile'):
            return context['activeFile']
        return None

    @staticmethod
    def get_open_files() -> list[str]:
        """Get list of currently open files in VS Code"""
        context = VSCodeContext.get_context()
        if context:
            # First try all open tabs
            if context.get('allOpenFiles'):
                return context['allOpenFiles']
            # Fallback to visible editors
            if context.get('openFiles'):
                return [f['path'] for f in context['openFiles']]
        return []

    @staticmethod
    def get_workspace_root() -> Optional[str]:
        """Get the VS Code workspace root"""
        context = VSCodeContext.get_context()
        if context and context.get('workspaceRoot'):
            return context['workspaceRoot']

        # Fallback: Check if we're in a git repository
        cwd = os.getcwd()
        current = Path(cwd)

        while current != current.parent:
            if (current / '.git').exists():
                return str(current)
            if (current / '.vscode').exists():
                return str(current)
            current = current.parent

        # Return current directory as fallback
        return cwd

    @staticmethod
    def has_extension_running() -> bool:
        """Check if VS Code extension is running and providing context"""
        context = VSCodeContext.get_context()
        return context is not None

    @staticmethod
    def read_file_content(file_path: str, max_lines: int = 1000) -> str:
        """Read file content with line limit"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append(f"\n... (truncated, {max_lines}+ lines)")
                        break
                    lines.append(line)
                return ''.join(lines)
        except Exception as e:
            return f"Error reading file: {str(e)}"
