"""Code editor for applying changes to files"""
import os
import re
import difflib
from pathlib import Path
from typing import Optional, List, Tuple


class CodeChange:
    """Represents a code change to be applied"""

    def __init__(self, file_path: str, old_code: str, new_code: str, description: str = ""):
        self.file_path = file_path
        self.old_code = old_code.strip()
        self.new_code = new_code.strip()
        self.description = description

    def apply(self) -> bool:
        """Apply the code change to the file"""
        try:
            # Read the current file content
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try exact match first
            if self.old_code in content:
                new_content = content.replace(self.old_code, self.new_code, 1)
            else:
                # Try with normalized whitespace
                normalized_old = self._normalize_for_matching(self.old_code)

                # Find the matching section with some flexibility
                import re
                # Create a pattern that's flexible with whitespace
                pattern = re.escape(normalized_old)
                pattern = re.sub(r'\\\s+', r'\\s+', pattern)  # Allow flexible whitespace

                match = re.search(pattern, content, re.MULTILINE)
                if not match:
                    return False

                # Replace the matched content
                start, end = match.span()
                new_content = content[:start] + self.new_code + content[end:]

            # Write back to file
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True
        except Exception as e:
            print(f"Error applying change: {e}")
            return False

    def _normalize_for_matching(self, code: str) -> str:
        """Normalize code for more flexible matching"""
        # Normalize line endings
        code = code.replace('\r\n', '\n').replace('\r', '\n')
        # Normalize multiple spaces to single space (but preserve indentation structure)
        lines = code.split('\n')
        normalized_lines = []
        for line in lines:
            # Keep leading whitespace structure but normalize the rest
            leading_spaces = len(line) - len(line.lstrip())
            rest = ' '.join(line.strip().split())
            normalized_lines.append(' ' * leading_spaces + rest)
        return '\n'.join(normalized_lines)

    def get_diff_lines(self) -> List[str]:
        """Get unified diff lines for display"""
        old_lines = self.old_code.splitlines(keepends=True)
        new_lines = self.new_code.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{self.file_path}",
            tofile=f"b/{self.file_path}",
            lineterm=''
        )

        return list(diff)


class CodeEditor:
    """Parses Sara's responses for code changes"""

    @staticmethod
    def extract_changes(response: str, active_file: Optional[str] = None) -> List[CodeChange]:
        """Extract code changes from Sara's response

        Looks for patterns like:
        ```edit:filename
        OLD:
        old code here
        NEW:
        new code here
        ```

        Or if active_file is provided and Sara just shows old/new:
        OLD:
        ```
        old code
        ```
        NEW:
        ```
        new code
        ```
        """
        changes = []

        # Pattern 1: Explicit edit blocks with filename
        pattern1 = r'```edit:(.+?)\nOLD:\n```(?:\w+)?\n(.*?)```\nNEW:\n```(?:\w+)?\n(.*?)```'
        matches = re.finditer(pattern1, response, re.DOTALL)

        for match in matches:
            file_path = match.group(1).strip()
            old_code = match.group(2).strip()
            new_code = match.group(3).strip()
            changes.append(CodeChange(file_path, old_code, new_code))

        # Pattern 2: Simple OLD/NEW pattern (uses active file)
        if active_file and not changes:
            pattern2 = r'OLD:\s*```(?:\w+)?\n(.*?)```\s*NEW:\s*```(?:\w+)?\n(.*?)```'
            matches = re.finditer(pattern2, response, re.DOTALL)

            for match in matches:
                old_code = match.group(1).strip()
                new_code = match.group(2).strip()
                changes.append(CodeChange(active_file, old_code, new_code))

        # Pattern 3: Change this/to this format
        if active_file and not changes:
            pattern3 = r'(?:Change|Replace):\s*```(?:\w+)?\n(.*?)```\s*(?:To|With):\s*```(?:\w+)?\n(.*?)```'
            matches = re.finditer(pattern3, response, re.DOTALL | re.IGNORECASE)

            for match in matches:
                old_code = match.group(1).strip()
                new_code = match.group(2).strip()
                changes.append(CodeChange(active_file, old_code, new_code))

        return changes

    @staticmethod
    def validate_change(change: CodeChange) -> Tuple[bool, str]:
        """Validate that a change can be applied

        Returns:
            (is_valid, error_message)
        """
        # Check file exists
        if not os.path.exists(change.file_path):
            return False, f"File not found: {change.file_path}"

        # Check file is readable
        try:
            with open(change.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return False, f"Cannot read file: {e}"

        # Check old code exists in file (try exact match first)
        if change.old_code in content:
            # Check old code appears only once
            if content.count(change.old_code) > 1:
                return False, "The code to replace appears multiple times in the file (need more unique context)"
            return True, ""

        # Try with flexible whitespace matching
        import re
        normalized_old = change._normalize_for_matching(change.old_code)
        pattern = re.escape(normalized_old)
        pattern = re.sub(r'\\\s+', r'\\s+', pattern)

        matches = list(re.finditer(pattern, content, re.MULTILINE))

        if not matches:
            # Provide helpful error with similar code
            lines = change.old_code.split('\n')
            first_line = lines[0].strip() if lines else ""

            if first_line and first_line in content:
                return False, (
                    f"Could not find exact match. Found similar code but with different "
                    f"whitespace/formatting. Try copying the exact code from the file."
                )
            else:
                return False, (
                    f"The code to replace was not found in the file. "
                    f"Make sure you're showing the EXACT code from the file (check line {change.file_path})"
                )

        if len(matches) > 1:
            return False, "The code to replace appears multiple times in the file (need more unique context)"

        return True, ""
