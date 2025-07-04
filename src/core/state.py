"""Migration state management for resumable operations."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Optional


@dataclass
class MigrationState:
    """Tracks the state of a migration operation for resumable transfers."""

    source_path: Path
    destination_path: Path
    total_size: int = 0
    copied_size: int = 0
    copied_files: Set[str] = field(default_factory=set)
    failed_files: Dict[str, str] = field(default_factory=dict)
    start_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert state to dictionary for JSON serialization."""
        return {
            "source_path": str(self.source_path),
            "destination_path": str(self.destination_path),
            "total_size": self.total_size,
            "copied_size": self.copied_size,
            "copied_files": list(self.copied_files),
            "failed_files": self.failed_files,
            "start_time": self.start_time.isoformat() if self.start_time else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MigrationState":
        """Create state from dictionary."""
        state = cls(
            source_path=Path(data["source_path"]),
            destination_path=Path(data["destination_path"]),
            total_size=data["total_size"],
            copied_size=data["copied_size"],
            copied_files=set(data["copied_files"]),
            failed_files=data["failed_files"],
        )
        if data["start_time"]:
            state.start_time = datetime.fromisoformat(data["start_time"])
        return state


class StateManager:
    """Manages saving and loading migration state."""

    def __init__(self, state_file: Path = Path(".migration_state.json")):
        self.state_file = state_file

    def save_state(self, state: MigrationState) -> None:
        """Save migration state to file."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(state.to_dict(), f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Cannot save state: {e}")

    def load_state(self) -> Optional[MigrationState]:
        """Load migration state from file."""
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
            return MigrationState.from_dict(data)
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Cannot load state: {e}")

    def cleanup_state(self) -> None:
        """Remove state file after successful migration."""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
        except OSError:
            pass  # Not critical if cleanup fails
