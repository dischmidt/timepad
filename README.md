# timepad — CLI Notebook & Log Manager

**timepad** is a lightweight command-line tool for managing timestamped notes and logs.
It creates files with standardized names (date/time + optional subject), opens them in your
preferred editor, and provides commands to list, view, edit, rename, and manage your entries.

---

## Purpose

Timepad helps you maintain a clear timeline of your work and thoughts. Each entry is
automatically timestamped and can include a descriptive subject. The consistent format
makes it easy to track what happened when, find related notes, and build a searchable
history of your activities. Perfect for documenting work sessions, tracking decisions,
recording meeting notes, or keeping a work log.

---

## Features

- **Structured filenames**  
  ```
  YYYY-MM-DD HH-MM-SS [subject].txt
  ```
  Examples:
  - `2025-09-24 11-19-47 start.txt`
  - `2025-09-24 11-19-47.txt` (no subject)

- **Automatic header**  
  New files are pre-filled with:
  ```
  # 2025-09-24 11:19:47 <username>
  ```

- **Editor integration**  
  Uses `$EDITOR` (default: `nano`). Works great with `vim`, `code -w`, etc.

- **Flexible storage (with CWD override)**  
  Directory precedence:
  1. `--dir <path>`
  2. `-c / --cwd` (force current directory; ignore env vars)
  3. `$TIMEPAD`
  4. `$LOG_DIR`
  5. current working directory  
  `~` and environment variables inside paths are expanded (e.g. `~/protocol`).

- **Shell mode**  
  Run `timepad` without a subcommand to enter an interactive shell with the same commands.

---

## Installation

```bash
pip install click click-shell rich
# optional: make the script executable and add to PATH
chmod +x timepad.py
```

---

## Filename & Header Format

- **Filename**: `YYYY-MM-DD HH-MM-SS [subject].txt`  
  (Note the *dashes* between time components.)
- **Header (first line)**: `# YYYY-MM-DD HH:MM:SS <username>`

---

## Commands

> For commands that take `<pattern>`, you can use any part of a filename (date, time, or subject).
> If multiple files match, timepad shows a numbered selection menu.

### Create & Edit

- `new [subject...]` [-at DATETIME]  
  Create a new entry and open in `$EDITOR`. Everything after `new` becomes the subject.
  Use `--at` to set a specific timestamp (format: 'YYYY-MM-DD HH:MM:SS').

  Examples:
  ```bash
  timepad new                      # => 2025-09-24 11-19-47.txt
  timepad new dataset fixes        # => 2025-09-24 11-19-47 dataset fixes.txt
  timepad new --at "2025-10-24 15:30:00" test  # Custom timestamp
  ```

### List & View

- `list [-a | -d]`  
  Show entries in a two-column table (timestamp and subject).
  - `-a` → ascending by date (oldest first) **[default]**
  - `-d` → descending by date (newest first)

- `ls`  
  List filenames only, sorted by date (ascending).

### View Contents

- `cat <pattern>`  
  Show contents of a matching file.

- `dump [-a | -d] [-s]`  
  Print all files in sequence.
  - `-a` → ascending (default)
  - `-d` → descending
  - `-s` → add separator lines between files

  Example:
  ```bash
  timepad dump -d -s  # Newest first with separators
  ```

### Edit & Remove

- `edit <pattern>`  
  Open matching file in `$EDITOR`.

- `rm <pattern>`  
  Delete matching file (asks for confirmation).

### File Management

- `mv <pattern>`  
  Rename matching file (prompts for new name).

- `rename <pattern>`  
  Change only the subject part (keeps timestamp).

- `cp <pattern>`  
  Copy to new filename (prompts for name).

- `bak <pattern>`  
  Create `.bak` copy (e.g. `2025-09-24 11-19-47 note.bak`).

### Configuration

- `config [--json]`  
  Show current settings (use --json for machine-readable output)

---

## Storage Location

Timepad uses the following priority order to determine where to store files:

1. `--dir ~/path`  (explicit directory path)
2. `-c/--cwd`     (force current directory, ignore env)
3. `$TIMEPAD`     (environment variable)
4. `$LOG_DIR`     (fallback environment variable) 
5. `CWD/.timepad` (if it exists)
6. `CWD`         (current directory)

Examples:
```bash
# Use specific directory
timepad --dir ~/notes new "meeting"

# Force current directory (ignore env vars)
timepad -c list

# Use environment variable
export TIMEPAD=~/protocol
timepad new "test"
```

> Path expansion: `~` and environment variables in paths are expanded
> (e.g., `~/protocol` becomes `/home/user/protocol`)

---

## Interactive Shell

Run `timepad` without arguments to enter shell mode:

```bash
timepad
Welcome to the Timepad shell. Type 'help' or 'exit'.
timepad> new first note
timepad> list -d        # Show newest first
timepad> cat 2025-09    # View entry matching date
timepad> edit note      # Edit entry matching "note"
timepad> dump -s        # Show all with separators
timepad> exit
```

---

## Examples

```bash
# Create and open a new entry with subject
timepad new import pipeline

# Show latest first
timepad list -d

# Print a specific day’s file when it’s unique
timepad cat 2025-09-24

# Dump all with visible separators
timepad dump -s

# Rename a file
timepad mv 11-19-47

# Make a backup
timepad bak import
```

---

## Notes

- If multiple files match your `<pattern>`, timepad will display a numbered list so you can choose the right one.
- The separator line used by `dump -s` is 80 hyphens:
  ```
  --------------------------------------------------------------------------------
  ```

---

## Requirements

- Python 3.8+
- Packages: `click`, `click-shell`, `rich`

