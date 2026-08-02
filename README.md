# Bullet Journal

A local-first command-line bullet journal written in Python.

The application stores journal entries as human-readable Markdown files, so the data remains portable and can be opened without the application.

## Features

- Create one journal file per day
- Add, edit and delete tasks
- Complete, reopen, cancel and migrate tasks
- Add, edit and delete notes
- Add, edit and delete events
- Review pending tasks from the previous day
- Search across journal files
- List existing journals
- Display pending tasks from multiple days
- Create backups before modifying journal files
- Restore the latest journal backup

## Task markers

- `[ ]` Open task
- `[x]` Completed task
- `[-]` Cancelled task
- `[>]` Migrated task

## Journal format

Daily journals are stored in the `journal` directory using filenames such as:

```text
2026-08-02.md
````

Each file follows this structure:


# Sunday, 02 August 2026

## Tasks

## Notes

## Events


## Requirements

* Python 3.12 or later
* No third-party Python packages are required

## Running the application

```bash
python3 main.py
```

## Running the tests

Run the complete test suite:

```bash
python3 -m unittest -b
```

Run the tests in verbose mode:

```bash
python3 -m unittest -v
```

## Project structure

```text
bullet-journal/
├── app.py
├── main.py
├── entry_actions.py
├── journal_actions.py
├── journal_parser.py
├── journal_storage.py
├── task_actions.py
├── terminal_ui.py
├── test_entry_actions.py
├── test_journal_actions.py
├── test_journal_parser.py
├── test_journal_storage.py
├── test_task_actions.py
├── test_terminal_ui.py
└── README.md
```

## Design principles

* Markdown files are the source of truth
* Journal data remains portable and human-readable
* Responsibilities are separated into focused modules
* Journal changes are validated and backed up
* Behaviour is protected by automated unit tests

````

Save it, then run:

```bash
python3 -m unittest -b
git status
````

If all 96 tests still pass, commit:

```bash
git add README.md
git commit -m "Add project documentation"
git push
```
