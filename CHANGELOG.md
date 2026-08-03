# Changelog

All notable changes to this project will be documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned

* Review terminal messages and menu consistency
* Perform a complete manual test of every menu option
* Prepare the first stable release

## [0.1.0] - 2026-08-03

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
