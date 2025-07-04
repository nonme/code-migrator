# Code Migrater

A smart file migration tool for code projects with intelligent filtering and progress tracking.

## Features

- **Smart Filtering**: Automatically excludes build artifacts, dependencies, and temporary files
- **Progress Tracking**: Visual progress bars with size-based tracking
- **Resumable Operations**: Can resume interrupted migrations
- **File Verification**: Optional hash verification for copied files
- **Async Performance**: Efficient async file copying

## Installation

### Using Poetry (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nonme/code-migrator.git
   cd code-migrator
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies:**
   ```bash
   poetry install
   ```

4. **Activate the virtual environment:**
   ```bash
   poetry env activate
   ```

### Alternative: Using Virtual Environment

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**
   ```bash
   # On Linux/macOS:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

## Usage

### Basic Usage

**Important: This tool COPIES directories (doesn't move them). Source remains unchanged.**

```bash
# Copy source directory into destination directory
python -m src.main /path/to/source /path/to/destination

# With verbose output
python -m src.main /path/to/source /path/to/destination --verbose

# Resume interrupted migration
python -m src.main /path/to/source /path/to/destination --resume

# Verify file hashes after copying
python -m src.main /path/to/source /path/to/destination --verify
```

### How it works

- **Source**: `/home/user/projects` (contains files and subdirectories)
- **Destination**: `/backup/`
- **Result**: Creates `/backup/projects/` with all contents of source
- **Source remains unchanged** - this is a copy operation, not a move

### Poetry Usage

```bash
# Run with Poetry
poetry run python -m src.main /path/to/source /path/to/destination

# Or activate environment first
poetry env activate
python -m src.main /path/to/source /path/to/destination
```

### Command Line Options

- `source`: Source directory to migrate (required)
- `destination`: Destination directory (required)
- `--resume`: Resume from previous migration state
- `--verbose`: Enable verbose logging
- `--verify`: Verify file hashes after copying (slower but more reliable)

## Examples

```bash
# Simple migration
python -m src.main ~/my-project ~/backup/my-project

# Migration with all options
python -m src.main ~/my-project ~/backup/my-project --verbose --verify --resume
```

## Development

### Running Tests

```bash
# With Poetry
poetry run pytest

# With virtual environment
python -m pytest
```

### Code Formatting

```bash
# With Poetry
poetry run black .
poetry run isort .

# With pip
black .
isort .
```

## Requirements

- Python 3.12+
- Dependencies are managed via Poetry or pip

## License

[Add your license here]