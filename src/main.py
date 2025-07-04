"""Main entry point for the smart file migrator."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from rich.console import Console

from .core.migrator import SmartFileMigrator


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Smart file migration tool for code projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/source /path/to/destination
  %(prog)s /path/to/source /path/to/destination --resume
  %(prog)s /path/to/source /path/to/destination --verbose --verify
        """,
    )

    parser.add_argument("source", type=Path, help="Source directory to migrate")

    parser.add_argument("destination", type=Path, help="Destination directory")

    parser.add_argument(
        "--resume", action="store_true", help="Resume from previous migration state"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify file hashes after copying (slower but more reliable)",
    )

    return parser


async def main() -> None:
    """Main entry point for the migration tool."""
    parser = create_argument_parser()
    args = parser.parse_args()

    console = Console()

    # Configure logging level
    if args.verbose:
        logging.getLogger("smart_migrator").setLevel(logging.DEBUG)

    # Create migrator
    migrator = SmartFileMigrator(console)

    # Show banner
    console.print("[bold cyan]Smart File Migration Tool[/bold cyan]")
    console.print(f"Source: {args.source}")
    console.print(f"Destination: {args.destination}")
    console.print(f"Resume: {'Yes' if args.resume else 'No'}")
    console.print(f"Verify: {'Yes' if args.verify else 'No'}")
    console.print()

    # Perform migration
    try:
        success = await migrator.migrate_directory(
            args.source, args.destination, resume=args.resume, verify_files=args.verify
        )

        if success:
            console.print("[bold green]Migration completed successfully![/bold green]")
            sys.exit(0)
        else:
            console.print("[bold red]Migration completed with errors[/bold red]")
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Migration interrupted by user[/yellow]")
        console.print("[cyan]You can resume later using --resume flag[/cyan]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
