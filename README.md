# Bullet Journal

A local-first Bullet Journal application written in Python, with both a graphical user interface and a command-line interface.

Journal data is stored as human-readable Markdown files on the local filesystem. The files remain portable, searchable and accessible without the application, avoiding dependence on a proprietary database or cloud service.

## Features

### Graphical interface

The Tkinter GUI provides:

* Create and browse daily journals
* Add, edit and delete tasks
* Complete, reopen, cancel and migrate tasks
* Add, edit and delete notes
* Add, edit and delete events
* Navigate between journal dates
* Jump directly to a specific date
* Browse all existing journals
* Search across journal files
* View pending tasks from multiple days
* Display task statistics for the current journal
* Restore journal backups
* Automatically create a journal only when content is first added
* Display journal availability/status
* Gracefully handle malformed journal files
* Scrollable journal view
* macOS trackpad and mouse-wheel support

### Command-line interface

The original CLI remains available and supports:

* Daily journal creation
* Task, note and event management
* Task migration
* Journal browsing
* Search
* Pending-task review
* Previous-day review
* Backup restoration
* Daily task statistics and completion progress

## Keyboard shortcuts

The GUI supports keyboard navigation on macOS, Linux and Windows.

| Action          | macOS     | Linux / Windows |
| --------------- | --------- | --------------- |
| Search journals | `Cmd + F` | `Ctrl + F`      |
| Previous day    | `Cmd + ←` | `Ctrl + ←`      |
| Next day        | `Cmd + →` | `Ctrl + →`      |

## Task markers

Tasks are stored using simple Markdown-compatible markers:

* `[ ]` Open task
* `[x]` Completed task
* `[-]` Cancelled task
* `[>]` Migrated task

For example:

```markdown
- [ ] Research project idea
- [x] Read documentation
- [-] Cancelled task
- [>] Migrated to another day
```

## Task summary

The application calculates task statistics for a journal.

The CLI displays a summary such as:

```text
Task summary:
Total: 4
Open: 2
Completed: 1
Cancelled: 0
Migrated: 1
Progress: [###-------] 33%
```

The GUI displays the same task states in a compact summary above the task controls.

Completion progress is calculated using open and completed tasks. Cancelled and migrated tasks are included in the total count but do not reduce completion progress.

## Journal format

Daily journals are stored in the `journal` directory using ISO-formatted filenames:

```text
2026-08-02.md
```

Each journal follows a deliberately simple structure:

```markdown
# Sunday, 02 August 2026

## Tasks

- [ ] Example task

## Notes

- Example note

## Events

- Example event
```

Markdown files are the source of truth. The GUI and CLI read and modify the same files.

## Backups

Before journal content is modified, the application maintains a backup of the previous journal state.

Backups use the `.bak` suffix:

```text
2026-08-02.md
2026-08-02.md.bak
```

Backups can be restored from either the CLI or GUI.

## Requirements

* Python 3.12 or later
* Tkinter for the graphical interface
* No third-party Python packages are required for normal operation

Tkinter is included with many Python installations, although some Linux distributions may package it separately.

## Running the graphical interface

From the project directory:

```bash
python3 gui.py
```

## Running the command-line interface

The original CLI remains available:

```bash
python3 main.py
```

Both interfaces operate on the same Markdown journal files.

## Running the tests

Run the complete test suite:

```bash
python3 -m unittest -b
```

Run the tests in verbose mode:

```bash
python3 -m unittest -v
```

The current automated test suite contains 114 tests covering journal parsing, storage, task and entry actions, terminal behaviour and journal queries.

## Project structure

```text
bullet-journal/
├── app.py
├── main.py
├── gui.py
├── gui_helpers.py
├── gui_task_actions.py
├── gui_note_actions.py
├── gui_event_actions.py
├── gui_backup_actions.py
├── entry_actions.py
├── journal_actions.py
├── journal_parser.py
├── journal_queries.py
├── journal_storage.py
├── task_actions.py
├── terminal_ui.py
├── version.py
├── test_entry_actions.py
├── test_journal_actions.py
├── test_journal_parser.py
├── test_journal_queries.py
├── test_journal_storage.py
├── test_task_actions.py
├── test_terminal_ui.py
├── CHANGELOG.md
├── pyproject.toml
└── README.md
```

The GUI-specific code is separated into focused modules rather than placing all application logic inside the main Tkinter window.

## Design principles

The project follows several deliberate design principles:

* **Local first** — journal data remains on the user's filesystem.
* **Portable data** — Markdown files can be read and edited without the application.
* **Simple storage** — no database is required.
* **Shared data model** — the CLI and GUI operate on the same journal files.
* **Separation of concerns** — parsing, storage, queries, terminal behaviour and GUI actions are separated into focused modules.
* **Defensive file handling** — journal changes are backed up and malformed journals are handled without terminating the GUI.
* **Testability** — core behaviour is protected by automated unit tests.
* **Minimal dependencies** — the application relies primarily on the Python standard library.

## Development status

The project began as a command-line Bullet Journal application and has since been extended with a Tkinter graphical interface.

The CLI provides the original stable workflow, while the GUI now exposes the main journal-management functionality through a desktop interface.

The next development stage is focused primarily on release polish, documentation and distribution rather than adding major core features.
