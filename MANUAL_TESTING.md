# Manual Testing Checklist

Run the application with:

```bash
python3 main.py
```

Use a temporary journal date or test data where possible.

## Startup

* [ ] The application starts without errors
* [ ] `Bullet Journal v0.1.0` is displayed
* [ ] The main menu is displayed correctly
* [ ] Invalid menu input produces a clear message
* [ ] The application can be exited normally

## Daily journal

* [ ] A journal can be created for the current day
* [ ] An existing daily journal can be opened
* [ ] The journal filename uses the expected date format
* [ ] The Markdown headings are created correctly

## Tasks

* [ ] Add a task
* [ ] Add several tasks
* [ ] Edit a task
* [ ] Complete a task
* [ ] Reopen a completed task
* [ ] Cancel a task
* [ ] Migrate a task
* [ ] Delete a task
* [ ] Invalid task numbers are handled correctly

## Task summary

* [ ] Total task count is correct
* [ ] Open task count is correct
* [ ] Completed task count is correct
* [ ] Cancelled task count is correct
* [ ] Migrated task count is correct
* [ ] Progress percentage is correct
* [ ] Cancelled tasks do not reduce progress
* [ ] Migrated tasks do not reduce progress
* [ ] The progress bar matches the percentage
* [ ] A journal with no tasks displays zero progress

## Notes

* [ ] Add a note
* [ ] Edit a note
* [ ] Delete a note
* [ ] Invalid note numbers are handled correctly

## Events

* [ ] Add an event
* [ ] Edit an event
* [ ] Delete an event
* [ ] Invalid event numbers are handled correctly

## Journal navigation

* [ ] List existing journals
* [ ] Open a journal from the list
* [ ] Search across journals
* [ ] Search with no matching results
* [ ] Display pending tasks from multiple days
* [ ] Review pending tasks from the previous day

## Backups

* [ ] Modifying a journal creates a backup
* [ ] The latest backup can be restored
* [ ] Restoring a backup recovers the expected content
* [ ] Attempting restoration without a backup is handled safely

## Data integrity

* [ ] Journal files remain valid Markdown
* [ ] Existing content is preserved after modifications
* [ ] Task markers remain valid
* [ ] Notes do not appear under events
* [ ] Events do not appear under notes
* [ ] The application does not modify unrelated journal files

## Automated verification

* [ ] Run the complete test suite:

```bash
python3 -m unittest -b
```

* [ ] All 106 tests pass
* [ ] GitHub Actions passes on the latest commit

## Final result

* [ ] All critical functions work
* [ ] No data-loss issue was found
* [ ] No unhandled exception was found
* [ ] User-facing messages are understandable
* [ ] The application is ready for release preparation
