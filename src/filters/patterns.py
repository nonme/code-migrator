"""File filtering patterns and logic."""

from pathlib import Path
from typing import Set


class FileFilter:
    """Handles file filtering based on patterns."""

    # Files and directories to exclude
    EXCLUDE_PATTERNS = {
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
        ".next",
        ".nuxt",
        "coverage",
        ".coverage",
        ".tox",
        ".venv",
        "venv",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        "*.tmp",
        "*.temp",
        ".sass-cache",
        ".parcel-cache",
        ".cache",
        "node_modules.bak",
        "bower_components",
        ".git/objects",
        ".git/refs",
        ".git/logs",
        "target",
        "bin",
        "obj",
        ".vs",
        ".vscode/settings.json",
        ".idea/workspace.xml",
        ".idea/tasks.xml",
    }

    # Files to explicitly include (even if they match exclude patterns)
    INCLUDE_PATTERNS = {
        ".env",
        ".env.local",
        ".env.development",
        ".env.production", 
        ".env.staging",
        ".env.test",
        ".env.example",
        ".env.template",
        ".env.sample",
        ".git",
        ".gitignore",
        ".gitmodules",
        ".gitattributes",
        ".dockerignore",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".editorconfig",
        ".prettierrc",
        "pyproject.toml",
        "poetry.lock",
        "requirements.txt",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "tsconfig.json",
        "tslint.json",
        "eslint.config.js",
        ".eslintrc.js",
        ".eslintrc.json",
        "jest.config.js",
        "babel.config.js",
        "webpack.config.js",
        "vite.config.ts",
        "tailwind.config.js",
        "postcss.config.js",
        "Makefile",
        "requirements-dev.txt",
        "setup.py",
        "setup.cfg",
        "tox.ini",
        ".pre-commit-config.yaml",
        ".github",
        "LICENSE",
        "README.md",
        "CHANGELOG.md",
        ".gitkeep",
        ".npmrc",
        ".yarnrc",
    }

    def __init__(
        self, additional_exclude: Set[str] = None, additional_include: Set[str] = None
    ):
        """Initialize filter with optional additional patterns."""
        self.exclude_patterns = self.EXCLUDE_PATTERNS.copy()
        self.include_patterns = self.INCLUDE_PATTERNS.copy()

        if additional_exclude:
            self.exclude_patterns.update(additional_exclude)
        if additional_include:
            self.include_patterns.update(additional_include)

    def should_exclude(self, path: Path) -> bool:
        """
        Determine if a path should be excluded from migration.

        Args:
            path: Path to check

        Returns:
            True if path should be excluded, False otherwise
        """
        path_str = str(path)
        name = path.name

        # Always include explicitly allowed patterns
        if any(
            pattern in name or pattern in path_str for pattern in self.include_patterns
        ):
            return False

        # Special case for .git directory - include structure but exclude some subdirs
        if ".git" in path.parts:
            git_excludes = {"objects", "refs", "logs"}
            if any(excluded in path.parts for excluded in git_excludes):
                return True

        # Check if any part of the path matches exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.startswith("*."):
                # Handle file extensions
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path.parts or pattern == name:
                return True
            elif pattern.endswith("*") and name.startswith(pattern[:-1]):
                return True

        return False
