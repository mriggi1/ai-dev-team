"""Bounded Python file tools that never execute generated code."""

from pathlib import Path
import json
import subprocess
import sys


class GeneratedWorkspace:
    """Read, write, and compile Python source within one output directory."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, path: str) -> Path:
        relative = Path(path)
        if relative.is_absolute() or relative.drive or ':' in path:
            raise ValueError('Use a relative Python file path.')
        target = (self.root / relative).resolve()
        if not target.is_relative_to(self.root) or target.suffix != '.py':
            raise ValueError('Only Python files inside the output directory are allowed.')
        if target.exists() and target.stat().st_nlink > 1:
            raise ValueError('Hard-linked files are not allowed.')
        return target

    def list_files(self) -> list[str]:
        """List Python files in the output directory."""
        return sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*.py')
                      if p.is_file())

    def read_file(self, path: str) -> str:
        """Read an existing Python file. Args: path: Relative Python file path."""
        target = self._path(path)
        if target.stat().st_size > 200_000:
            raise ValueError('File exceeds the 200 KB limit.')
        return target.read_text(encoding='utf-8')

    def write_file(self, path: str, content: str) -> str:
        """Write complete Python source to a relative path inside the output directory."""
        target = self._path(path)
        if len(content.encode('utf-8')) > 200_000:
            raise ValueError('File exceeds the 200 KB limit.')
        if not target.exists() and len(self.list_files()) >= 20:
            raise ValueError('The output directory is limited to 20 Python files.')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
        return f'Written: {path}'

    def check_syntax(self) -> dict:
        """Compile all saved Python files without executing them or creating bytecode."""
        files = self.list_files()
        errors = []
        for path in files:
            try:
                compile(self.read_file(path), path, 'exec')
            except (SyntaxError, ValueError, OSError) as exc:
                errors.append(f'{path}: {exc}')
        return {'ok': bool(files) and not errors, 'files': files, 'errors': errors}

    def check_static_analysis(self) -> dict:
        """Check saved Python files with Ruff F821/F823 without executing or fixing code."""
        try:
            files = self.list_files()
            if not files:
                return {'ok': False, 'issues': [], 'errors': ['No Python files found.']}
            # Validate every path before passing explicit filenames to Ruff.
            paths = [str(self._path(path)) for path in files]
            result = subprocess.run(
                [sys.executable, '-I', '-m', 'ruff', 'check', '--isolated',
                 '--no-cache', '--ignore-noqa', '--select', 'F821,F823',
                 '--output-format', 'json', '--', *paths],
                capture_output=True, text=True, encoding='utf-8',
                timeout=30, check=False,
            )
            if result.returncode not in (0, 1):
                return {'ok': False, 'issues': [], 'errors': [
                    result.stderr.strip() or f'Ruff exited with code {result.returncode}.']}
            diagnostics = json.loads(result.stdout)
            issues = [
                {'file': str(Path(item['filename']).relative_to(self.root)),
                 'line': item['location']['row'],
                 'column': item['location']['column'],
                 'rule': item['code'], 'message': item['message']}
                for item in diagnostics
            ]
            return {'ok': result.returncode == 0 and not issues,
                    'issues': issues, 'errors': []}
        except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError) as exc:
            return {'ok': False, 'issues': [], 'errors': [f'Static analysis failed: {exc}']}

    def source(self) -> str:
        """Return the saved source, with filename comments for the reviewer."""
        return '\n\n'.join(f'# File: {path}\n{self.read_file(path)}'
                           for path in self.list_files())
