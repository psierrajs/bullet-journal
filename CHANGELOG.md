# Changelog

All notable changes to this project will be documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

## [1.2.2] - 2026-08-13

### Fixed

- Removed a duplicate artifact download declaration from the GitHub Release workflow.

## [1.2.1] - 2026-08-13

### Fixed

- Fixed the automated GitHub Release workflow by checking out the repository before creating a release.
- Updated GitHub artifact actions to current versions.

## [1.2.0] - 2026-08-13

### Added

- Installable Python package structure under `bullet_journal`
- Installed command-line launcher: `bullet-journal`
- Installed graphical launcher: `bullet-journal-gui`
- Platform-independent Python wheel distribution
- PyInstaller-based standalone desktop builds
- Automated GitHub Actions builds for macOS, Windows and Linux
- Downloadable build artifacts for all three supported desktop platforms
- Automated GitHub Release workflow for version tags
- Platform-specific application data directories
- Open Journal Folder action in the graphical interface
- Journal export to ZIP archives
- Automated tests for platform-specific data paths
- Automated tests for opening journal directories
- Automated tests for journal export behaviour

### Changed

- Reorganized application modules into the `bullet_journal` Python package
- Converted internal application imports to package-relative imports
- Reduced top-level `main.py` and `gui.py` to thin application launchers
- Updated project metadata for versioned Python packaging
- Configured setuptools to package only the `bullet_journal` application package
- Journal storage no longer depends on the current working directory
- Journal files are now stored in operating-system-appropriate application data directories
- Updated README with wheel installation, cross-platform builds, data locations and export documentation
- Expanded automated test coverage from 114 tests to 125 tests

### Distribution

- macOS builds produce a standalone `.app` bundle
- Windows builds produce a standalone `.exe`
- Linux builds produce a standalone executable
- Python distributions produce a `py3-none-any` wheel
- The same application source and Markdown journal format are shared across all supported operating systems
- Current macOS development builds remain unsigned and unnotarized

### Design

- Application logic is now separated from platform-specific launch and distribution concerns
- Journal data remains local-first, portable and human-readable
- Operating-system-specific behaviour is isolated in dedicated path and packaging logic
- Distribution artifacts can be generated automatically from the same source repository

## [1.2.0] - 2026-08-13

### Added

- Installable Python package structure under `bullet_journal`
- Installed command-line launcher: `bullet-journal`
- Installed graphical launcher: `bullet-journal-gui`
- Platform-independent Python wheel distribution
- PyInstaller-based standalone desktop builds
- Automated GitHub Actions builds for macOS, Windows and Linux
- Downloadable build artifacts for all three supported desktop platforms
- Automated GitHub Release workflow for version tags
- Platform-specific application data directories
- Open Journal Folder action in the graphical interface
- Journal export to ZIP archives
- Automated tests for platform-specific data paths
- Automated tests for opening journal directories
- Automated tests for journal export behaviour

### Changed

- Reorganized application modules into the `bullet_journal` Python package
- Converted internal application imports to package-relative imports
- Reduced top-level `main.py` and `gui.py` to thin application launchers
- Updated project metadata for versioned Python packaging
- Configured setuptools to package only the `bullet_journal` application package
- Journal storage no longer depends on the current working directory
- Journal files are now stored in operating-system-appropriate application data directories
- Updated README with wheel installation, cross-platform builds, data locations and export documentation
- Expanded automated test coverage from 114 tests to 125 tests

### Distribution

- macOS builds produce a standalone `.app` bundle
- Windows builds produce a standalone `.exe`
- Linux builds produce a standalone executable
- Python distributions produce a `py3-none-any` wheel
- The same application source and Markdown journal format are shared across all supported operating systems
- Current macOS development builds remain unsigned and unnotarized

### Design

- Application logic is now separated from platform-specific launch and distribution concerns
- Journal data remains local-first, portable and human-readable
- Operating-system-specific behaviour is isolated in dedicated path and packaging logic
- Distribution artifacts can be generated automatically from the same source repository

## [1.1.0] - 2026-08-10

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
