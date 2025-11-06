"""File system context gathering for Sara"""
import os
from pathlib import Path
from typing import Optional


class FileContext:
    # Common directories to exclude
    EXCLUDE_DIRS = {
        'node_modules', '.git', '__pycache__', '.venv', 'venv',
        'env', 'dist', 'build', '.next', '.nuxt', 'target',
        'coverage', '.pytest_cache', '.mypy_cache', 'vendor'
    }

    # File extensions to include for code context
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
        '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift',
        '.kt', '.scala', '.sh', '.bash', '.zsh', '.sql', '.html',
        '.css', '.scss', '.sass', '.json', '.yaml', '.yml', '.xml',
        '.md', '.txt', '.toml', '.ini', '.cfg', '.conf'
    }

    @staticmethod
    def get_directory_structure(root_path: str, max_depth: int = 3) -> str:
        """Get a tree-like structure of the directory"""
        lines = [f"Directory structure of {root_path}:\n"]

        def walk_dir(path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return

            try:
                entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                dirs = [e for e in entries if e.is_dir() and e.name not in FileContext.EXCLUDE_DIRS]
                files = [e for e in entries if e.is_file() and e.suffix in FileContext.CODE_EXTENSIONS]

                for i, entry in enumerate(dirs + files):
                    is_last = i == len(dirs + files) - 1
                    current_prefix = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{current_prefix}{entry.name}\n")

                    if entry.is_dir() and depth < max_depth:
                        extension = "    " if is_last else "│   "
                        walk_dir(entry, prefix + extension, depth + 1)
            except PermissionError:
                pass

        walk_dir(Path(root_path))
        return ''.join(lines)

    @staticmethod
    def get_relevant_files(
        root_path: str,
        query: Optional[str] = None,
        max_files: int = 10
    ) -> list[tuple[str, str]]:
        """Get relevant files from the repository

        Returns list of (file_path, file_content) tuples
        """
        files_data = []
        root = Path(root_path)

        def should_include_file(file_path: Path) -> bool:
            # Check if file extension is in our list
            if file_path.suffix not in FileContext.CODE_EXTENSIONS:
                return False

            # Check if any excluded directory is in the path
            parts = file_path.parts
            if any(excluded in parts for excluded in FileContext.EXCLUDE_DIRS):
                return False

            return True

        # Collect all relevant files
        all_files = []
        try:
            for file_path in root.rglob('*'):
                if file_path.is_file() and should_include_file(file_path):
                    all_files.append(file_path)
        except PermissionError:
            pass

        # If we have a query, try to prioritize matching files
        if query:
            query_lower = query.lower()
            scored_files = []
            for file_path in all_files:
                score = 0
                file_name_lower = file_path.name.lower()

                # Score based on filename match
                if query_lower in file_name_lower:
                    score += 10

                # Score based on file type relevance
                if any(keyword in query_lower for keyword in ['test', 'spec']):
                    if 'test' in file_name_lower or 'spec' in file_name_lower:
                        score += 5

                scored_files.append((score, file_path))

            # Sort by score and take top files
            scored_files.sort(reverse=True, key=lambda x: x[0])
            selected_files = [f for _, f in scored_files[:max_files]]
        else:
            # Just take the most recent files
            all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            selected_files = all_files[:max_files]

        # Read file contents
        for file_path in selected_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(50000)  # Limit to ~50KB per file
                    relative_path = file_path.relative_to(root)
                    files_data.append((str(relative_path), content))
            except (UnicodeDecodeError, PermissionError):
                continue

        return files_data

    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """Get metadata about a file"""
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}

        stat = path.stat()
        return {
            "name": path.name,
            "extension": path.suffix,
            "size_bytes": stat.st_size,
            "modified": stat.st_mtime,
            "is_code": path.suffix in FileContext.CODE_EXTENSIONS
        }
