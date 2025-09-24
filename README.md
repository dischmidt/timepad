# timepad — CLI Notebook & Log Manager

**timepad** is a small, fast command-line tool for timestamped notes/logs (“protocols”).
It creates files named by date/time (and optional subject), opens them in your editor,
and provides convenient commands to list, view, dump, edit, rename, copy, and back up entries.

---

## Purpose

Timepad helps you record what happened, when it happened, and why. Each note begins with the current date and time, plus a short subject, so your work forms a clear timeline and context. You can start a note for a task, return to it later, and quickly find related notes for the same project or day. Reading, renaming, copying, or safely backing up entries is simple. Use it to document steps, capture ideas, track progress, and assemble a dependable story of your decisions and results.

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

> In all commands that take `<pattern>`, you can pass a **full** filename or **any substring** of it
> (e.g., the date or a unique keyword). If multiple files match, timepad shows a numbered list to choose from.

### Create

- `new [subject...]`  
  Create a new entry, open in `$EDITOR`. Everything after `new` becomes the **subject** in the filename.

  Examples:
  ```bash
  timepad new                      # => 2025-09-24 11-19-47.txt
  timepad new dataset fixes        # => 2025-09-24 11-19-47 dataset fixes.txt
  ```

### List

- `list [-a | -d]`  
  Show entries in a table. **Two columns only**:
  - **Date/Time** (from filename)
  - **Subject** (filename without date/time and without `.txt`)

  Flags:
  - `-a` → ascending (oldest first) **[default]**
  - `-d` → descending (newest first)

### View / Dump

- `cat <pattern>`  
  Print the contents of a single matching file to stdout.

- `dump [-a | -d] [-s]`  
  Print **all** files to stdout in sequence.  
  Flags:
  - `-a` → ascending (default)
  - `-d` → descending
  - `-s` → **add a separator line** between files (80 hyphens)

  Example:
  ```bash
  timepad dump -d -s
  ```

### Edit / Remove

- `edit <pattern>`  
  Open a matching file in `$EDITOR`.

- `rm <pattern>`  
  Delete a matching file (**with confirmation**).

### Rename / Copy / Backup

- `mv <pattern>`  
  Rename a file (you’ll be prompted for the new filename).

- `cp <pattern>`  
  Copy a file (you’ll be prompted for the new filename).

- `bak <pattern>`  
  Create a `.bak` copy next to the file (e.g., `2025-09-24 11-19-47 note.bak`).

### List Filenames Only

- `ls`  
  Print filenames only (like `ls`), sorted ascending by date/time.

---

## Directory Selection

You can control where files live:

- Force current directory and ignore env vars:
  ```bash
  timepad -c list
  ```
- Specify a directory explicitly:
  ```bash
  timepad --dir ~/protocol new "today"
  ```
- Or set an environment variable:
  ```bash
  export TIMEPAD=~/protocol
  # or
  export LOG_DIR=~/protocol
  ```

> `~` and variables inside paths are expanded, e.g. `~/protocol` → `/home/you/protocol`.

---

## Shell Mode

Run `timepad` with no subcommand:

```bash
timepad
timepad> new first note
timepad> list -d
timepad> dump -s
timepad> edit 2025-09-24
timepad> rm note
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

