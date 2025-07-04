"""Smart file migration tool for code projects."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.migrator import SmartFileMigrator
from .core.state import MigrationState

__all__ = ["SmartFileMigrator", "MigrationState"]
