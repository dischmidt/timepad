# Timepad – A CLI Notebook and Log Manager

**Timepad** is a command-line tool for managing personal logs, notes, and protocol entries.  
It creates timestamped text files, organizes them in a directory, and provides commands to list, view, edit, rename, copy, and back up these entries.

## Features

- **Structured filenames**  
  Entries are stored as text files with names like:
  ```
  YYYY-MM-DD HH-MM-SS [subject].txt
  ```  
  The timestamp is always included; the subject is optional.  
  Example:
  - `2025-09-24 11-19-47 start.txt`  
  - `2025-09-24 11-19-47.txt`  

- **Automatic header**  
  Each new file is pre-filled with a header containing the timestamp and the current login username:
  ```text
  # 2025-09-24 11:19:47 dave
  ```

- **Editor integration**  
  Files are opened in the editor defined by `$EDITOR` (default: `nano`).

- **Flexible storage**  
  Timepad stores entries in:
  1. The directory passed with `--dir`  
  2. Or the path set in `$TIMEPAD`  
  3. Or `$LOG_DIR`  
  4. Or the current working directory  

## Commands

- **new [subject...]**  
  Create a new entry with the current timestamp and optional subject.  
  Opens directly in the editor.

- **list [-a | -d]**  
  Show all entries in a table.  
  - `-a` sorts entries **ascending** (oldest first). This is the default.  
  - `-d` sorts entries **descending** (newest first).

- **cat <pattern>**  
  Print the contents of an entry.  
  `<pattern>` can be:
  - The full filename  
  - A part of the filename (for example, only the date or a keyword from the subject)  
  If multiple matches exist, you can select the right file from a numbered list.

- **dump [-a | -d]**  
  Print all entries in sequence (ascending or descending).

- **edit <pattern>**  
  Open a matching entry in the editor. Works the same way as `cat` when matching filenames.

- **rm <pattern>**  
  Delete a matching entry after confirmation.

- **mv <pattern>**  
  Rename a matching entry. You will be prompted for the new filename.

- **cp <pattern>**  
  Copy a matching entry. You will be prompted for the new filename.

- **bak <pattern>**  
  Create a backup of the entry with the extension `.bak`.

## Use Cases

- Keep daily notes and personal logs.  
- Track tasks, corrections, or datasets with timestamps.  
- Maintain lightweight protocol records directly in the terminal.

