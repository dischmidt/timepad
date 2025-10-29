# AI Coding Assistant Instructions for Timepad

## Project Overview
Timepad is a CLI notebook/logging tool built with Click and Rich libraries. It manages timestamped text entries in a configurable directory structure.

## Key Components & Architecture

### Core Concepts
- **Entries**: Text files with filename format `YYYY-MM-DD HH-MM-SS Subject.txt` 
- **Base Directory Resolution**: Follows priority: `--dir > -c/--cwd > $TIMEPAD > $LOG_DIR > CWD/.timepad (if exists) > CWD`
- **Working Directory**: Can be configured via CLI flags, environment variables, or defaults to current directory

### Main Components
1. CLI Framework (`click`/`click-shell`)
   - Main CLI interface with subcommands
   - Interactive shell mode when no subcommand provided
2. Entry Management
   - `Entry` dataclass for parsing/representing entries
   - File operations (create, read, edit, rename, delete)
3. Rich UI Components
   - Tables for listing entries
   - Colored output and formatting
   - Interactive prompts for user confirmation

## Development Workflow

### Dependencies
```bash
pip install click click-shell rich
```

### Key Files
- `__main__.py`: Core implementation containing all commands and logic
- Configuration precedence handled by `resolve_base_dir()` function

### Testing Guidelines
- Test directory resolution with various flag/env combinations
- Verify filename parsing/formatting in `parse_entry()`/`_make_filename()`
- Check interactive prompts handle user input correctly

## Project Conventions

### Time Format Handling
- Filenames use hyphenated time format: `HH-MM-SS`
- Internal/display format uses colons: `HH:MM:SS` 
- See `_normalize_query_time_to_hyphens()` for conversion logic

### Error Handling
- Rich console used for user feedback with color coding:
  - Red: Errors
  - Yellow: Warnings/cancellations
  - Green: Success messages
  - Cyan: Information

### File Operations
- Always use UTF-8 encoding
- Create parent directories as needed
- Prompt for confirmation on destructive operations
- Preserve file metadata on copy operations

## Integration Points

### Environment Variables
- `$EDITOR`/`$VISUAL`: Editor command
- `$TIMEPAD`: Primary directory override
- `$LOG_DIR`: Fallback directory
- `$USER`/`$USERNAME`: For entry headers

### External Tools
- Uses system editor via `$EDITOR`/`$VISUAL` (fallback: nano)
- File operations via standard Python os/shutil modules

Remember to use absolute paths and handle shell command construction carefully (see `_editor_info()` and `open_in_editor()`).

## Common Patterns
1. Command Implementation:
   ```python
   @cli.command(help="...")
   @click.argument/option(...)
   @click.pass_context
   def cmd(ctx, ...):
       _cmd_implementation(ctx.obj, ...)
   ```

2. User Interaction:
   ```python
   if Confirm.ask("...", default=False):
       # Proceed with action
   ```

3. File Selection:
   ```python
   e = resolve_by_query(base_dir, query)
   if not e:
       return
   # Proceed with entry
   ```