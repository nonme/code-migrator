"""Progress tracking utilities."""

import logging
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table


class ProgressTracker:
    """Tracks and displays migratision progress."""

    def __init__(self, console: Console):
        self.console = console
        self.logger = logging.getLogger(__name__)

    def calculate_directory_size(self, path: Path, filter_func) -> int:
        """
        Calculate total size of directory with filtering.

        Args:
            path: Directory path
            filter_func: Function to determine if path should be excluded

        Returns:
            Total size in bytes
        """
        total_size = 0

        try:
            for item in path.rglob("*"):
                if item.is_file() and not filter_func(item):
                    try:
                        total_size += item.stat().st_size
                    except (OSError, PermissionError) as e:
                        self.logger.warning(f"Cannot access {item}: {e}")
        except (OSError, PermissionError) as e:
            self.logger.error(f"Cannot access directory {path}: {e}")

        return total_size

    def show_migration_results(self, state) -> None:
        """Display migration results summary."""
        table = Table(title="Migration Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        total_files = len(state.copied_files) + len(state.failed_files)
        success_rate = (
            (len(state.copied_files) / total_files * 100) if total_files > 0 else 0
        )

        table.add_row("Total Files", str(total_files))
        table.add_row("Copied Successfully", str(len(state.copied_files)))
        table.add_row("Failed", str(len(state.failed_files)))
        table.add_row("Success Rate", f"{success_rate:.1f}%")
        table.add_row("Total Size", f"{state.total_size:,} bytes")
        table.add_row("Copied Size", f"{state.copied_size:,} bytes")

        if state.start_time:
            duration = datetime.now() - state.start_time
            table.add_row("Duration", str(duration))

        self.console.print(table)

        # Show failed files if any
        if state.failed_files:
            self.console.print("\n[red]Failed files:[/red]")
            for file_path, error in state.failed_files.items():
                self.console.print(f"  {file_path}: {error}")
