#!/usr/bin/env python3
"""
Timepad CLI

A small notebook/log tool based on click + click-shell + rich.

Filename format: "YYYY-MM-DD HH-MM-SS Subject.txt" (note the dashes in time)

Commands:
  new [subject...]   – create a new entry and open it in $EDITOR (or nano)
  list [-a|-d]       – show entries as a table (ascending/descending)
  cat  <pattern>     – print file content by filename or part of it
  dump [-a|-d]       – print all entries in sequence
  edit <pattern>     – open a file in the editor by pattern
  rm   <pattern>     – delete a file by pattern (with confirmation)
  mv   <pattern>     – rename an entry after selecting it uniquely
  cp   <pattern>     – copy an entry to a new filename
  bak  <pattern>     – create a .bak copy next to the file
  ls                 - list filenames

Directory resolution priority:
  --dir option > $TIMEPAD > $LOG_DIR > current working directory

Dependencies: click, click-shell, rich
"""
from __future__ import annotations

import os
import sys
import shlex
import glob
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import click
from click_shell import shell
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import box

console = Console()

FILENAME_DT_LEN = 19  # len("YYYY-MM-DD HH-MM-SS")
DISPLAY_DT_FORMAT = "%Y-%m-%d %H:%M:%S"   # used inside the file header
FILENAME_DT_FORMAT = "%Y-%m-%d %H-%M-%S"  # used in filenames (time with dashes)
DEFAULT_EDITOR = "nano"


@dataclass
class Entry:
    path: str
    dt: datetime
    subject: str

    @property
    def filename(self) -> str:
        return os.path.basename(self.path)


def resolve_base_dir(dir_opt: Optional[str], ignore_env: bool = False) -> str:
    # Precedence: --dir > -c > $TIMEPAD > $LOG_DIR > CWD
    if dir_opt:
        chosen = dir_opt
    elif ignore_env:
        chosen = os.getcwd()
    else:
        chosen = (
            os.environ.get("TIMEPAD")
            or os.environ.get("LOG_DIR")
            or os.getcwd()
        )
    return os.path.abspath(os.path.expanduser(os.path.expandvars(chosen)))


def parse_entry(path: str) -> Optional[Entry]:
    name = os.path.basename(path)
    if not name.lower().endswith(".txt"):
        return None
    if len(name) < FILENAME_DT_LEN + 5:  # dt + space + a.txt
        return None
    dt_str = name[:FILENAME_DT_LEN]
    dt = None
    for fmt in (FILENAME_DT_FORMAT, DISPLAY_DT_FORMAT):
        try:
            dt = datetime.strptime(dt_str, fmt)
            break
        except ValueError:
            continue
    if dt is None:
        return None
    subject = name[FILENAME_DT_LEN + 1 : -4]
    return Entry(path=path, dt=dt, subject=subject)


def scan_entries(base_dir: str) -> List[Entry]:
    entries: List[Entry] = []
    for p in glob.glob(os.path.join(base_dir, "*.txt")):
        e = parse_entry(p)
        if e:
            entries.append(e)
    return entries


def sort_entries(entries: List[Entry], ascending: bool = True) -> List[Entry]:
    return sorted(entries, key=lambda e: e.dt, reverse=not ascending)


def open_in_editor(path: str) -> int:
    editor = os.environ.get("EDITOR", DEFAULT_EDITOR).strip() or DEFAULT_EDITOR
    try:
        cmd = shlex.split(editor) + [path]
    except ValueError:
        cmd = [editor, path]
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        console.print(f"[red]Editor '{editor}' not found.[/red]")
        return 1


def pick_from_matches(matches: List[Entry]) -> Optional[Entry]:
    if not matches:
        console.print("[yellow]No matches found.[/yellow]")
        return None
    if len(matches) == 1:
        return matches[0]
    table = Table(title="Multiple matches – select one", box=box.SIMPLE)
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Date/Time", style="green")
    table.add_column("Subject", style="magenta")
    sorted_matches = sort_entries(matches)
    for i, e in enumerate(sorted_matches, start=1):
        table.add_row(str(i), e.dt.strftime(DISPLAY_DT_FORMAT), e.subject)
    console.print(table)
    while True:
        choice = Prompt.ask("Number", default="1")
        if not choice.isdigit():
            console.print("[red]Please enter a number.[/red]")
            continue
        idx = int(choice)
        if 1 <= idx <= len(sorted_matches):
            return sorted_matches[idx - 1]
        console.print("[red]Invalid choice.[/red]")


def resolve_by_query(base_dir: str, query: str) -> Optional[Entry]:
    query_lower = query.lower()
    matches = [e for e in scan_entries(base_dir) if query_lower in e.filename.lower()]
    return pick_from_matches(matches)


@click.group(invoke_without_command=True)
@click.option("--dir", "dir_opt", type=click.Path(file_okay=False, dir_okay=True),
              help="Working directory (default: --dir > -c > $TIMEPAD > $LOG_DIR > CWD)")
@click.option("-c", "--cwd", is_flag=True,
              help="Use current directory; ignore $TIMEPAD and $LOG_DIR")
@click.pass_context
def cli(ctx: click.Context, dir_opt: Optional[str], cwd: bool):
    """Timepad CLI. Without a subcommand, an interactive shell is started."""
    ctx.ensure_object(dict)
    ctx.obj["base_dir"] = resolve_base_dir(dir_opt, ignore_env=cwd)
    if ctx.invoked_subcommand is None:
        start_shell(ctx.obj)


def start_shell(obj: dict):
    @shell(prompt="timepad> ", intro="Welcome to the Timepad shell. Type 'help' or 'exit'.")
    def sh():
        pass

    @sh.command(help="Create a new entry and open it in the editor")
    @click.argument("subject_parts", nargs=-1)
    @click.pass_context
    def new(ctx, subject_parts: tuple[str, ...]):
        _cmd_new(obj, subject=" ".join(subject_parts).strip())

    @sh.command(help="Show entries as a table")
    @click.option("-a", "ascending", is_flag=True, default=True, help="Ascending (default)")
    @click.option("-d", "descending", is_flag=True, help="Descending")
    @click.pass_context
    def list(ctx, ascending: bool, descending: bool):
        asc = ascending if not descending else False
        _cmd_list(obj, asc)

    @sh.command(help="Show file content (by part of filename)")
    @click.argument("query", nargs=1)
    @click.pass_context
    def cat(ctx, query):
        _cmd_cat(obj, query)

    @sh.command(help="Dump all entries in sequence")
    @click.option("-a", "ascending", is_flag=True, default=True, help="Ascending (default)")
    @click.option("-d", "descending", is_flag=True, help="Descending")
    @click.pass_context
    def dump(ctx, ascending: bool, descending: bool):
        asc = ascending if not descending else False
        _cmd_dump(obj, asc)

    @sh.command(help="Edit a file in the editor (by part of filename)")
    @click.argument("query", nargs=1)
    @click.pass_context
    def edit(ctx, query):
        _cmd_edit(obj, query)

    @sh.command(help="Delete a file (by part of filename)")
    @click.argument("query", nargs=1)
    @click.pass_context
    def rm(ctx, query):
        _cmd_rm(obj, query)

    @sh.command(help="Rename an entry (by part of filename)")
    @click.argument("query", nargs=1)
    @click.pass_context
    def mv(ctx, query):
        _cmd_mv(obj, query)

    @sh.command(help="Copy an entry to a new filename (by part of filename)")
    @click.argument("query", nargs=1)
    @click.pass_context
    def cp(ctx, query):
        _cmd_cp(obj, query)

    @sh.command(help="Create a .bak backup next to the file")
    @click.argument("query", nargs=1)
    @click.pass_context
    def bak(ctx, query):
        _cmd_bak(obj, query)

    @sh.command(help="List filenames")
    @click.pass_context
    def ls(ctx):
        _cmd_ls(obj)

    sh()


@cli.command(help="Create a new entry and open it in the editor")
@click.argument("subject_parts", nargs=-1)
@click.option("--at", "when", type=str, default=None, help="Manually set timestamp (format: 'YYYY-MM-DD HH:MM:SS') for the file header only")
@click.pass_context
def new(ctx, subject_parts: tuple[str, ...], when: Optional[str]):
    _cmd_new(ctx.obj, when=when, subject=" ".join(subject_parts).strip())


@cli.command(name="list", help="Show entries as a table")
@click.option("-a", "ascending", is_flag=True, default=True, help="Ascending (default)")
@click.option("-d", "descending", is_flag=True, help="Descending")
@click.pass_context
def list_cmd(ctx, ascending: bool, descending: bool):
    asc = ascending if not descending else False
    _cmd_list(ctx.obj, asc)


@cli.command(help="Show file content")
@click.argument("query", nargs=1)
@click.pass_context
def cat(ctx, query: str):
    _cmd_cat(ctx.obj, query)


@cli.command(help="Dump all entries")
@click.option("-a", "ascending", is_flag=True, default=True, help="Ascending (default)")
@click.option("-d", "descending", is_flag=True, help="Descending")
@click.pass_context
def dump(ctx, ascending: bool, descending: bool):
    asc = ascending if not descending else False
    _cmd_dump(ctx.obj, asc)


@cli.command(help="Edit a file in the editor")
@click.argument("query", nargs=1)
@click.pass_context
def edit(ctx, query: str):
    _cmd_edit(ctx.obj, query)


@cli.command(help="Delete a file")
@click.argument("query", nargs=1)
@click.pass_context
def rm(ctx, query: str):
    _cmd_rm(ctx, query)


@cli.command(help="Rename an entry")
@click.argument("query", nargs=1)
@click.pass_context
def mv(ctx, query: str):
    _cmd_mv(ctx.obj, query)


@cli.command(help="Copy an entry to a new filename")
@click.argument("query", nargs=1)
@click.pass_context
def cp(ctx, query: str):
    _cmd_cp(ctx.obj, query)


@cli.command(help="Create a .bak backup of an entry")
@click.argument("query", nargs=1)
@click.pass_context
def bak(ctx, query: str):
    _cmd_bak(ctx.obj, query)


@cli.command(help="List filenames in the working directory (like 'ls')")
@click.pass_context
def ls(ctx):
    _cmd_ls(ctx.obj)

# ----------------- Implementations -----------------

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _make_filename(ts: datetime, subject: str | None) -> str:
    base = ts.strftime(FILENAME_DT_FORMAT)
    if subject:
        return f"{base} {subject}.txt"
    return f"{base}.txt"


def _cmd_new(obj: dict, when: Optional[str] = None, subject: Optional[str] = None):
    base_dir = obj["base_dir"]
    _ensure_dir(base_dir)
    if when:
        try:
            ts = datetime.strptime(when, DISPLAY_DT_FORMAT)
        except ValueError:
            console.print(f"[red]Invalid datetime format. Expected: {DISPLAY_DT_FORMAT}[/red]")
            return
    else:
        ts = datetime.now()
    filename = _make_filename(ts, (subject or "").strip() or None)
    path = os.path.join(base_dir, filename)
    username = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
    if os.path.exists(path):
        console.print(f"[yellow]Note: File already exists and will be opened.[/yellow]")
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {ts.strftime(DISPLAY_DT_FORMAT)} {username}\n\n")
    console.print(Panel.fit(f"Editing: [bold]{os.path.basename(path)}[/bold]", style="cyan"))
    rc = open_in_editor(path)
    if rc != 0:
        sys.exit(rc)


def _cmd_list(obj: dict, ascending: bool):
    base_dir = obj["base_dir"]
    entries = sort_entries(scan_entries(base_dir), ascending=ascending)

    table = Table(title=f"Entries in {base_dir}", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Date/Time", style="green", no_wrap=True)
    table.add_column("Subject", style="magenta")

    for e in entries:
        table.add_row(e.dt.strftime(DISPLAY_DT_FORMAT), e.subject)

    if not entries:
        console.print("[yellow]No entries found.[/yellow]")
    else:
        console.print(table)


def _cmd_cat(obj: dict, query: str):
    base_dir = obj["base_dir"]
    e = resolve_by_query(base_dir, query)
    if not e:
        return
    with open(e.path, "r", encoding="utf-8") as f:
        sys.stdout.write(f.read())


def _cmd_dump(obj: dict, ascending: bool):
    base_dir = obj["base_dir"]
    entries = sort_entries(scan_entries(base_dir), ascending=ascending)
    first = True
    for e in entries:
        with open(e.path, "r", encoding="utf-8") as f:
            content = f.read()
            if not first and not content.endswith("\n"):
                sys.stdout.write("\n")
            sys.stdout.write(content)
            first = False


def _cmd_edit(obj: dict, query: str):
    base_dir = obj["base_dir"]
    e = resolve_by_query(base_dir, query)
    if not e:
        return
    console.print(Panel.fit(f"Editing: [bold]{e.filename}[/bold]", style="cyan"))
    rc = open_in_editor(e.path)
    if rc != 0:
        sys.exit(rc)


def _cmd_rm(ctx_or_obj, query: str):
    # Accept either ctx (with .obj) or obj directly for shell/cli symmetry
    obj = ctx_or_obj if isinstance(ctx_or_obj, dict) else ctx_or_obj.obj
    base_dir = obj["base_dir"]
    e = resolve_by_query(base_dir, query)
    if not e:
        return
    if Confirm.ask(f"Really delete file '[bold]{e.filename}[/bold]'?", default=False):
        try:
            os.remove(e.path)
            console.print(f"[green]Deleted:[/green] {e.filename}")
        except OSError as ex:
            console.print(f"[red]Error while deleting:[/red] {ex}")


def _prompt_new_filename(default_name: str) -> Optional[str]:
    new_name = Prompt.ask("New filename", default=default_name).strip()
    if not new_name:
        console.print("[yellow]Aborted: empty filename.[/yellow]")
        return None
    return new_name


def _cmd_mv(obj: dict, query: str):
    base_dir = obj["base_dir"]
    e = resolve_by_query(base_dir, query)
    if not e:
        return
    new_name = _prompt_new_filename(e.filename)
    if not new_name:
        return
    new_path = os.path.join(base_dir, new_name)
    if os.path.exists(new_path):
        if not Confirm.ask("Target exists. Overwrite?", default=False):
            console.print("[yellow]Move cancelled.[/yellow]")
            return
    try:
        os.replace(e.path, new_path)
        console.print(f"[green]Renamed to:[/green] {os.path.basename(new_path)}")
    except OSError as ex:
        console.print(f"[red]Error while renaming:[/red] {ex}")


def _cmd_cp(obj: dict, query: str):
    base_dir = obj["base_dir"]
    e = resolve_by_query(base_dir, query)
    if not e:
        return
    new_name = _prompt_new_filename(e.filename)
    if not new_name:
        return
    new_path = os.path.join(base_dir, new_name)
    if os.path.exists(new_path):
        if not Confirm.ask("Target exists. Overwrite?", default=False):
            console.print("[yellow]Copy cancelled.[/yellow]")
            return
    try:
        shutil.copy2(e.path, new_path)
        console.print(f"[green]Copied to:[/green] {os.path.basename(new_path)}")
    except OSError as ex:
        console.print(f"[red]Error while copying:[/red] {ex}")


def _cmd_bak(obj: dict, query: str):
    base_dir = obj["base_dir"]
    e = resolve_by_query(base_dir, query)
    if not e:
        return
    root, ext = os.path.splitext(e.filename)
    bak_name = f"{root}.bak"
    bak_path = os.path.join(base_dir, bak_name)
    if os.path.exists(bak_path):
        if not Confirm.ask("Backup exists. Overwrite?", default=False):
            console.print("[yellow]Backup cancelled.[/yellow]")
            return
    try:
        shutil.copy2(e.path, bak_path)
        console.print(f"[green]Backup created:[/green] {bak_name}")
    except OSError as ex:
        console.print(f"[red]Error while creating backup:[/red] {ex}")

def _cmd_ls(obj: dict):
    """List filenames in the working directory (like 'ls')."""
    base_dir = obj["base_dir"]
    entries = sort_entries(scan_entries(base_dir), ascending=True)
    for e in entries:
        click.echo(e.filename)

if __name__ == "__main__":
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted by user[/dim]")

