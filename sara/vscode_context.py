"""VS Code integration to detect open files and workspace context"""
import os
import json
import subprocess
from pathlib import Path
from typing import Optional


class VSCodeContext:
    @staticmethod
    def get_open_files() -> list[str]:
        """Get list of currently open files in VS Code"""
        # Try to get open files from VS Code via osascript (macOS)
        try:
            script = '''
            tell application "Visual Studio Code"
                set windowCount to count of windows
                set openFiles to {}
                repeat with w from 1 to windowCount
                    tell window w
                        set docPath to path of document 1
                        if docPath is not missing value then
                            set end of openFiles to docPath
                        end if
                    end tell
                end repeat
                return openFiles
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                # Parse the result (comma-separated file paths)
                files = result.stdout.strip().split(', ')
                return [f.strip() for f in files if f.strip()]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fallback: Check for recent VS Code workspace state files
        return VSCodeContext._get_files_from_workspace_state()

    @staticmethod
    def _get_files_from_workspace_state() -> list[str]:
        """Try to get open files from VS Code workspace state"""
        vscode_dir = Path.home() / 'Library' / 'Application Support' / 'Code' / 'User' / 'workspaceStorage'

        if not vscode_dir.exists():
            return []

        try:
            # Look for the most recent workspace.json
            workspace_files = []
            for ws_dir in vscode_dir.iterdir():
                if ws_dir.is_dir():
                    workspace_json = ws_dir / 'workspace.json'
                    state_json = ws_dir / 'state.vscdb'
                    if workspace_json.exists():
                        workspace_files.append(workspace_json)

            if workspace_files:
                # Get most recently modified
                latest = max(workspace_files, key=lambda p: p.stat().st_mtime)
                with open(latest) as f:
                    data = json.load(f)
                    folder = data.get('folder')
                    if folder:
                        # This gives us the workspace folder
                        return [folder]
        except (json.JSONDecodeError, PermissionError):
            pass

        return []

    @staticmethod
    def get_workspace_root() -> Optional[str]:
        """Try to determine the current VS Code workspace root"""
        # First check if we're in a git repository
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
