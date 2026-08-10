# Changelog

All notable changes to this project will be documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Tkinter graphical user interface
- Single-window journal navigation
- Previous, Today and Next date navigation
- Direct navigation to a specific journal date
- Journal browser for opening existing journal files
- Search window for finding text across journals
- Pending-task window for reviewing open tasks across multiple days
- GUI support for adding, editing and deleting tasks
- GUI support for completing, reopening, cancelling and migrating tasks
- GUI support for adding, editing and deleting notes
- GUI support for adding, editing and deleting events
- Task summary display in the GUI
- Lazy journal creation when content is first added
- Journal availability/status indicator
- GUI backup restoration
- Keyboard shortcuts for search and date navigation
- Scrollable journal interface
- macOS trackpad and mouse-wheel scrolling support
- Graceful handling of malformed or unreadable journal files
- Journal-query module for reusable search and pending-task logic
- Additional automated tests for journal-query behaviour
- GUI screenshot and updated project documentation

### Changed

- Refactored GUI code into focused modules for tasks, notes, events, backups and shared helpers
- Updated README to document both GUI and CLI workflows
- Updated project structure documentation to reflect the GUI architecture
- Improved the application from CLI-only to a shared CLI and desktop-GUI workflow
- Removed duplicate Previous Day navigation control

### Design

- GUI and CLI operate on the same Markdown journal files
- GUI-specific actions are separated from core journal logic
- Journal data remains local-first and human-readable
- Core journal-query behaviour remains independently testable
- Desktop functionality continues to rely primarily on the Python standard library

## [1.0.0] - 2026-08-03

### Added

* Daily Markdown journal creation
* Task creation, editing and deletion
* Task completion and reopening
* Task cancellation and migration
* Note creation, editing and deletion
* Event creation, editing and deletion
* Previous-day task review
* Journal search
* Journal listing
* Pending-task display across multiple days
* Automatic backups before journal modifications
* Restoration of the latest journal backup
* Daily task statistics
* Task-completion percentage
* Terminal progress bar
* Application version display
* Automated unit-test suite
* GitHub Actions continuous integration
* Project documentation and roadmap

### Design

* Local-first data storage
* Human-readable Markdown files as the source of truth
* Separation of application, storage, parsing and terminal-interface responsibilities
* No third-party Python runtime dependencies
