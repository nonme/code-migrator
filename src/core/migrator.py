"""Core migration functionality."""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import aiofiles
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TransferSpeedColumn,
)

from src.utils.hashing import FileHasher

from .state import MigrationState, StateManager
from ..filters.patterns import FileFilter
from ..utils.progress import ProgressTracker


class SmartFileMigrator:
    """
    Smart file migrator with intelligent filtering and progress tracking.

    Features:
    - Excludes build artifacts and dependencies
    - Includes configuration and version control files
    - Tracks progress by file size
    - Supports resumable operations
    """

    def __init__(self, console: Console):
        self.console = console
        self.logger = self._setup_logging()
        self.state_manager = StateManager()
        self.file_filter = FileFilter()
        self.progress_tracker = ProgressTracker(console)
        self.file_hasher = FileHasher()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the migration process."""
        logger = logging.getLogger("smart_migrator")
        logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        handler = logging.FileHandler("migration.log")
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    async def _copy_file_async(self, source: Path, destination: Path) -> bool:
        """
        Copy a single file asynchronously with verification.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create destination directory if it doesn't exist
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Copy file in chunks
            async with aiofiles.open(source, "rb") as src:
                async with aiofiles.open(destination, "wb") as dst:
                    while chunk := await src.read(64 * 1024):  # 64KB chunks
                        await dst.write(chunk)

            # Copy metadata
            shutil.copystat(source, destination)

            # Verify copy (optional, can be disabled for performance)
            # if not self.file_hasher.verify_copy(source, destination):
            #     self.logger.warning(f"Hash mismatch for {source}")
            #     return False

            return True

        except (OSError, PermissionError) as e:
            self.logger.error(f"Failed to copy {source} to {destination}: {e}")
            return False

    def _collect_files_to_copy(
        self, source: Path, destination: Path, copied_files: set
    ) -> List[Tuple[Path, Path]]:
        """
        Collect files that need to be copied.

        Args:
            source: Source directory
            destination: Destination directory
            copied_files: Set of already copied files

        Returns:
            List of (source_path, destination_path) tuples
        """
        files_to_copy = []

        for file_path in source.rglob("*"):
            if file_path.is_file() and not self.file_filter.should_exclude(file_path):
                relative_path = file_path.relative_to(source)
                if str(relative_path) not in copied_files:
                    files_to_copy.append((file_path, destination / relative_path))

        return files_to_copy

    async def migrate_directory(
        self,
        source: Path,
        destination: Path,
        resume: bool = False,
        verify_files: bool = False,
    ) -> bool:
        """
        Migrate directory with smart filtering and progress tracking.

        Args:
            source: Source directory path
            destination: Destination directory path
            resume: Whether to resume from previous state
            verify_files: Whether to verify file hashes after copying

        Returns:
            True if migration successful, False otherwise
        """
        # Validate paths
        if not source.exists():
            self.console.print(f"[red]Source directory {source} does not exist[/red]")
            return False

        if not source.is_dir():
            self.console.print(f"[red]Source {source} is not a directory[/red]")
            return False

        # Load or create state
        state = None
        if resume:
            try:
                state = self.state_manager.load_state()
                if state and (
                    state.source_path != source or state.destination_path != destination
                ):
                    self.console.print(
                        "[yellow]Previous migration state doesn't match current paths[/yellow]"
                    )
                    state = None
            except RuntimeError as e:
                self.console.print(f"[red]Error loading state: {e}[/red]")
                return False

        # Create destination as source_name inside destination path
        actual_destination = destination / source.name
        
        if not state:
            state = MigrationState(source, actual_destination)
            state.start_time = datetime.now()

            # Calculate total size
            self.console.print("[cyan]Calculating total size...[/cyan]")
            with self.console.status("[cyan]Scanning directories..."):
                state.total_size = self.progress_tracker.calculate_directory_size(
                    source, self.file_filter.should_exclude
                )

            self.console.print(f"[green]Total size: {state.total_size:,} bytes[/green]")

        # Collect files to copy
        files_to_copy = []

        with self.console.status("[cyan]Collecting files..."):
            files_to_copy = self._collect_files_to_copy(
                source, actual_destination, state.copied_files
            )

        if not files_to_copy:
            self.console.print("[green]All files already copied![/green]")
            self.state_manager.cleanup_state()
            return True

        # Create progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:

            task = progress.add_task(
                "Copying files...", total=state.total_size, completed=state.copied_size
            )

            # Copy files
            for source_file, dest_file in files_to_copy:
                try:
                    file_size = source_file.stat().st_size

                    # Copy file
                    success = await self._copy_file_async(source_file, dest_file)

                    if success:
                        # Optional verification
                        if verify_files and not self.file_hasher.verify_copy(
                            source_file, dest_file
                        ):
                            self.logger.warning(f"Hash mismatch for {source_file}")
                            success = False

                    if success:
                        # Update state
                        relative_path = str(source_file.relative_to(source))
                        state.copied_files.add(relative_path)
                        state.copied_size += file_size

                        # Update progress
                        progress.update(task, advance=file_size)

                        # Save state periodically
                        if len(state.copied_files) % 100 == 0:
                            self.state_manager.save_state(state)
                    else:
                        relative_path = str(source_file.relative_to(source))
                        state.failed_files[relative_path] = "Copy failed"

                except (OSError, PermissionError) as e:
                    relative_path = str(source_file.relative_to(source))
                    state.failed_files[relative_path] = str(e)
                    self.logger.error(f"Failed to process {source_file}: {e}")
                except KeyboardInterrupt:
                    # Save state before exiting
                    self.state_manager.save_state(state)
                    raise

        # Save final state
        self.state_manager.save_state(state)

        # Show results
        self.progress_tracker.show_migration_results(state)

        # Cleanup if successful
        if not state.failed_files:
            self.state_manager.cleanup_state()
            return True

        return False
