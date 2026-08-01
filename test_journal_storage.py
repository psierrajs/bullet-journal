import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from journal_storage import (
    append_line,
    create_daily_journal,
    insert_before_section,
    replace_task,
    restore_backup,
    write_journal,
)

class DailyJournalCreationTests(unittest.TestCase):

    def test_creates_daily_journal_with_correct_template(self):
        journal_date = date(2026, 8, 1)

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            create_daily_journal(
                journal_file,
                journal_date
            )

            self.assertTrue(journal_file.exists())

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

    def test_does_not_overwrite_existing_journal(self):
        journal_date = date(2026, 8, 1)

        existing_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Existing task\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                existing_content,
                encoding="utf-8"
            )

            create_daily_journal(
                journal_file,
                journal_date
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                existing_content
            )

class JournalWritingTests(unittest.TestCase):

    def test_writes_valid_journal_content(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Test the application\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            result = write_journal(
                journal_file,
                content
            )

            self.assertTrue(result)
            self.assertTrue(journal_file.exists())

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                content
            )

    def test_rejects_invalid_journal_content(self):
        invalid_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            result = write_journal(
                journal_file,
                invalid_content
            )

            self.assertFalse(result)
            self.assertFalse(journal_file.exists())

    def test_creates_backup_of_existing_journal(self):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Original task\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        updated_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Original task\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            write_journal(
                journal_file,
                updated_content
            )

            backup_file = journal_file.with_suffix(
                journal_file.suffix + ".bak"
            )

            self.assertTrue(backup_file.exists())

            backup_content = backup_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                backup_content,
                original_content
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                updated_content
            )

    def test_removes_temporary_file_after_writing(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            write_journal(
                journal_file,
                content
            )

            temporary_file = journal_file.with_suffix(
                journal_file.suffix + ".tmp"
            )

            self.assertFalse(temporary_file.exists())

class LineAppendingTests(unittest.TestCase):

    def test_appends_event_to_end_of_journal(self):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
            "- 18:00 Meeting\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            append_line(
                original_content,
                "- 18:00 Meeting\n",
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

    def test_removes_extra_blank_lines_before_appending(self):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n\n\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
            "- 18:00 Meeting\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            append_line(
                original_content,
                "- 18:00 Meeting\n",
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

class RestoreBackupTests(unittest.TestCase):

    @patch("journal_storage.pause")
    @patch("builtins.input", return_value="y")
    def test_restores_backup(
        self,
        mock_input,
        mock_pause
    ):
        current_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        backup_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            backup_file = journal_file.with_suffix(
                journal_file.suffix + ".bak"
            )

            journal_file.write_text(
                current_content,
                encoding="utf-8"
            )

            backup_file.write_text(
                backup_content,
                encoding="utf-8"
            )

            restore_backup(journal_file)

            restored_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                restored_content,
                backup_content
            )

            mock_input.assert_called_once_with(
                "Restore this backup? Current changes will be replaced. [y/N]: "
            )

            mock_pause.assert_called_once()

    @patch("journal_storage.pause")
    @patch("builtins.input", return_value="n")
    def test_keeps_current_journal_when_restore_is_cancelled(
        self,
        mock_input,
        mock_pause
    ):
        current_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        backup_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            backup_file = journal_file.with_suffix(
                journal_file.suffix + ".bak"
            )

            journal_file.write_text(
                current_content,
                encoding="utf-8"
            )

            backup_file.write_text(
                backup_content,
                encoding="utf-8"
            )

            restore_backup(journal_file)

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                current_content
            )

            mock_pause.assert_called_once()

    @patch("journal_storage.pause")
    def test_handles_missing_backup(
        self,
        mock_pause
    ):
        current_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                current_content,
                encoding="utf-8"
            )

            restore_backup(journal_file)

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                current_content
            )

            mock_pause.assert_called_once()

class SectionInsertionTests(unittest.TestCase):

    def test_inserts_task_before_notes_section(self):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            notes_start = original_content.find("## Notes")

            insert_before_section(
                original_content,
                notes_start,
                "- [ ] Buy seeds\n",
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

    def test_inserts_note_before_events_section(self):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n"
            "- Greenhouse was warm\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            events_start = original_content.find("## Events")

            insert_before_section(
                original_content,
                events_start,
                "- Greenhouse was warm\n",
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

class TaskReplacementTests(unittest.TestCase):

    def test_replaces_selected_task(self):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n"
            "- [ ] Test the pump\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n"
            "- [ ] Test the pump\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            replace_task(
                original_content,
                "- [ ] Buy seeds",
                "- [x] Buy seeds",
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )
    def test_replaces_only_first_matching_task(self):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Water plants\n"
            "- [ ] Water plants\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Water plants\n"
            "- [ ] Water plants\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            replace_task(
                original_content,
                "- [ ] Water plants",
                "- [x] Water plants",
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )
if __name__ == "__main__":
    unittest.main()

