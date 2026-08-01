import tempfile
import unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch
from pathlib import Path
from io import StringIO

from journal_storage import (
    append_line,
    create_daily_journal,
    insert_before_section,
    replace_task,
    restore_backup,
    write_journal,
)

from terminal_ui import (
    select_line,
    select_task,
)

from journal_actions import (
    list_journals,
    list_pending_tasks,
    search_journals,
    review_previous_day,
    view_journal,
)


from task_actions import (
    add_task,
    cancel_task,
    complete_task,
    delete_task,
    edit_task,
    migrate_task,
    reopen_task,
)

from entry_actions import (
    add_event,
    add_note,
    delete_event,
    delete_note,
    edit_event,
    edit_note,
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

class TaskSelectionTests(unittest.TestCase):

    @patch("builtins.input", return_value="2")
    def test_selects_task_by_number(self, mock_input):
        task_lines = [
            "- [ ] Buy seeds",
            "- [ ] Test the pump",
            "- [x] Prepare soil",
        ]

        result = select_task(
            task_lines,
            "Enter the task number: "
        )

        self.assertEqual(
            result,
            "- [ ] Test the pump"
        )

        mock_input.assert_called_once_with(
            "Enter the task number: "
        )

    @patch("builtins.input", return_value="abc")
    def test_returns_none_for_non_numeric_input(self, mock_input):
        task_lines = [
            "- [ ] Buy seeds",
            "- [ ] Test the pump",
        ]

        result = select_task(
            task_lines,
            "Enter the task number: "
        )

        self.assertIsNone(result)

    @patch("builtins.input", return_value="5")
    def test_returns_none_for_number_outside_range(
        self,
        mock_input
    ):
        task_lines = [
            "- [ ] Buy seeds",
            "- [ ] Test the pump",
        ]

        result = select_task(
            task_lines,
            "Enter the task number: "
        )

        self.assertIsNone(result)

    @patch("builtins.input", return_value="0")
    def test_returns_none_for_zero(self, mock_input):
        task_lines = [
            "- [ ] Buy seeds",
            "- [ ] Test the pump",
        ]

        result = select_task(
            task_lines,
            "Enter the task number: "
        )

        self.assertIsNone(result)

    def test_returns_none_when_task_list_is_empty(self):
        result = select_task(
            [],
            "Enter the task number: "
        )

        self.assertIsNone(result)

class CompleteTaskTests(unittest.TestCase):

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_completes_selected_task(
        self,
        mock_input,
        mock_pause
    ):
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

        task_lines = [
            "- [ ] Buy seeds",
            "- [ ] Test the pump",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            complete_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

            mock_input.assert_called_once_with(
                "Enter the number of the completed task: "
            )

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_does_not_change_already_completed_task(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [x] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            complete_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                original_content
            )

            mock_pause.assert_called_once()

class ReopenTaskTests(unittest.TestCase):

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_reopens_completed_task(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [x] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            reopen_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_reopens_cancelled_task(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [-] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [-] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            reopen_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_does_not_change_open_task(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [ ] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            reopen_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                original_content
            )

            mock_pause.assert_called_once()

class CancelTaskTests(unittest.TestCase):

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_cancels_open_task(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [-] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [ ] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            cancel_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_does_not_change_already_cancelled_task(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [-] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [-] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            cancel_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                original_content
            )

            mock_pause.assert_called_once()

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_does_not_cancel_completed_task(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [x] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            cancel_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                original_content
            )

            mock_pause.assert_called_once()

class EditTaskTests(unittest.TestCase):

    @patch("task_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "Buy vegetable seeds"]
    )
    def test_edits_open_task(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy vegetable seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [ ] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            edit_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

            mock_pause.assert_called_once()
    @patch("task_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "Purchase vegetable seeds"]
    )
    def test_preserves_completed_task_marker(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Purchase vegetable seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [x] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            edit_task(
                original_content,
                task_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

    @patch("task_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", ""]
    )
    def test_does_not_edit_when_new_text_is_empty(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [ ] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            edit_task(
                original_content,
                task_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            mock_pause.assert_called_once()

class DeleteTaskTests(unittest.TestCase):

    @patch("task_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "y"]
    )
    def test_deletes_selected_task(
        self,
        mock_input,
        mock_pause
    ):
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
            "- [ ] Test the pump\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [ ] Buy seeds",
            "- [ ] Test the pump",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            delete_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

            mock_pause.assert_called_once()

    @patch("task_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "n"]
    )
    def test_keeps_task_when_deletion_is_cancelled(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [ ] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            delete_task(
                original_content,
                task_lines,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                original_content
            )

            mock_pause.assert_called_once()

    @patch("task_actions.pause")
    def test_does_nothing_when_task_list_is_empty(
        self,
        mock_pause
    ):
        original_content = (
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
                original_content,
                encoding="utf-8"
            )

            delete_task(
                original_content,
                [],
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            mock_pause.assert_called_once()

class MigrateTaskTests(unittest.TestCase):

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_migrates_open_task_to_next_day(
        self,
        mock_input,
        mock_pause
    ):
        today = date(2026, 8, 1)

        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_today_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [>] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [ ] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            journal_file = (
                journal_folder
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            migrate_task(
                original_content,
                task_lines,
                journal_file,
                journal_folder,
                today
            )

            tomorrow_file = (
                journal_folder
                / "2026-08-02.md"
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_today_content
            )

            self.assertTrue(tomorrow_file.exists())

            tomorrow_content = tomorrow_file.read_text(
                encoding="utf-8"
            )

            self.assertIn(
                "- [ ] Buy seeds",
                tomorrow_content
            )

            mock_pause.assert_called_once()

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_does_not_migrate_completed_task(
        self,
        mock_input,
        mock_pause
    ):
        today = date(2026, 8, 1)

        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [x] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            journal_file = (
                journal_folder
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            migrate_task(
                original_content,
                task_lines,
                journal_file,
                journal_folder,
                today
            )

            tomorrow_file = (
                journal_folder
                / "2026-08-02.md"
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            self.assertFalse(tomorrow_file.exists())
            mock_pause.assert_called_once()

    @patch("task_actions.pause")
    @patch("builtins.input", return_value="1")
    def test_does_not_migrate_cancelled_task(
        self,
        mock_input,
        mock_pause
    ):
        today = date(2026, 8, 1)

        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [-] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        task_lines = [
            "- [-] Buy seeds",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            journal_file = (
                journal_folder
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            migrate_task(
                original_content,
                task_lines,
                journal_file,
                journal_folder,
                today
            )

            tomorrow_file = (
                journal_folder
                / "2026-08-02.md"
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            self.assertFalse(tomorrow_file.exists())
            mock_pause.assert_called_once()

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

class AddNoteTests(unittest.TestCase):

    @patch(
        "builtins.input",
        side_effect=["Greenhouse was warm", ""]
    )
    def test_adds_note_before_events_section(
        self,
        mock_input
    ):
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

            events_start = original_content.find(
                "## Events"
            )

            add_note(
                original_content,
                events_start,
                journal_file
            )

            saved_content = journal_file.read_text(
                encoding="utf-8"
            )

            self.assertEqual(
                saved_content,
                expected_content
            )

    @patch(
        "builtins.input",
        side_effect=[
            "Greenhouse was warm",
            "Water level was low",
            ""
        ]
    )
    def test_adds_multiple_notes(
        self,
        mock_input
    ):
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
            "- Greenhouse was warm\n"
            "- Water level was low\n\n"
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

            events_start = original_content.find(
                "## Events"
            )

            add_note(
                original_content,
                events_start,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

    @patch("builtins.input", return_value="")
    def test_does_not_add_empty_note(
        self,
        mock_input
    ):
        original_content = (
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
                original_content,
                encoding="utf-8"
            )

            events_start = original_content.find(
                "## Events"
            )

            add_note(
                original_content,
                events_start,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

class AddEventTests(unittest.TestCase):

    @patch(
        "builtins.input",
        side_effect=["18:00 Meeting", ""]
    )
    def test_adds_event_to_end_of_journal(
        self,
        mock_input
    ):
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

            add_event(
                original_content,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

    @patch(
        "builtins.input",
        side_effect=[
            "18:00 Meeting",
            "20:00 Water plants",
            ""
        ]
    )
    def test_adds_multiple_events(
        self,
        mock_input
    ):
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
            "- 20:00 Water plants\n"
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

            add_event(
                original_content,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

    @patch("builtins.input", return_value="")
    def test_does_not_add_empty_event(
        self,
        mock_input
    ):
        original_content = (
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
                original_content,
                encoding="utf-8"
            )

            add_event(
                original_content,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

class EditNoteTests(unittest.TestCase):

    @patch("entry_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "Greenhouse was very warm"]
    )
    def test_edits_selected_note(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- Greenhouse was warm\n"
            "- Water level was low\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- Greenhouse was very warm\n"
            "- Water level was low\n\n"
            "## Events\n"
        )

        note_lines = [
            "- Greenhouse was warm",
            "- Water level was low",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            edit_note(
                original_content,
                note_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

            mock_pause.assert_called_once()

class EditNoteTests(unittest.TestCase):

    @patch("entry_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "Greenhouse was very warm"]
    )
    def test_edits_selected_note(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- Greenhouse was warm\n"
            "- Water level was low\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- Greenhouse was very warm\n"
            "- Water level was low\n\n"
            "## Events\n"
        )

        note_lines = [
            "- Greenhouse was warm",
            "- Water level was low",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            edit_note(
                original_content,
                note_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

            mock_pause.assert_called_once()

    @patch("entry_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", ""]
    )
    def test_does_not_edit_note_when_new_text_is_empty(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- Greenhouse was warm\n\n"
            "## Events\n"
        )

        note_lines = [
            "- Greenhouse was warm",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            edit_note(
                original_content,
                note_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            mock_pause.assert_called_once()

class DeleteNoteTests(unittest.TestCase):

    @patch("entry_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "y"]
    )
    def test_deletes_selected_note(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- Greenhouse was warm\n"
            "- Water level was low\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- Water level was low\n\n"
            "## Events\n"
        )

        note_lines = [
            "- Greenhouse was warm",
            "- Water level was low",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            delete_note(
                original_content,
                note_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

            mock_pause.assert_called_once()

    @patch("entry_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "n"]
    )
    def test_keeps_note_when_deletion_is_cancelled(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- Greenhouse was warm\n\n"
            "## Events\n"
        )

        note_lines = [
            "- Greenhouse was warm",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            delete_note(
                original_content,
                note_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            mock_pause.assert_called_once()

    @patch("entry_actions.pause")
    def test_does_nothing_when_note_list_is_empty(
        self,
        mock_pause
    ):
        original_content = (
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
                original_content,
                encoding="utf-8"
            )

            delete_note(
                original_content,
                [],
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            mock_pause.assert_called_once()

class EditEventTests(unittest.TestCase):

    @patch("entry_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "19:00 Project meeting"]
    )
    def test_edits_selected_event(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
            "- 18:00 Meeting\n"
            "- 20:00 Water plants\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
            "- 19:00 Project meeting\n"
            "- 20:00 Water plants\n"
        )

        event_lines = [
            "- 18:00 Meeting",
            "- 20:00 Water plants",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            edit_event(
                original_content,
                event_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

            mock_pause.assert_called_once()

    @patch("entry_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", ""]
    )
    def test_does_not_edit_event_when_new_text_is_empty(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
            "- 18:00 Meeting\n"
        )

        event_lines = [
            "- 18:00 Meeting",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            edit_event(
                original_content,
                event_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            mock_pause.assert_called_once()

    @patch("entry_actions.pause")
    def test_does_nothing_when_event_list_is_empty(
        self,
        mock_pause
    ):
        original_content = (
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
                original_content,
                encoding="utf-8"
            )

            edit_event(
                original_content,
                [],
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            mock_pause.assert_called_once()

class DeleteEventTests(unittest.TestCase):

    @patch("entry_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "y"]
    )
    def test_deletes_selected_event(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
            "- 18:00 Meeting\n"
            "- 20:00 Water plants\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
            "- 20:00 Water plants\n"
        )

        event_lines = [
            "- 18:00 Meeting",
            "- 20:00 Water plants",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            delete_event(
                original_content,
                event_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

            mock_pause.assert_called_once()

    @patch("entry_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "n"]
    )
    def test_keeps_event_when_deletion_is_cancelled(
        self,
        mock_input,
        mock_pause
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
            "- 18:00 Meeting\n"
        )

        event_lines = [
            "- 18:00 Meeting",
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_file = (
                Path(temporary_directory)
                / "2026-08-01.md"
            )

            journal_file.write_text(
                original_content,
                encoding="utf-8"
            )

            delete_event(
                original_content,
                event_lines,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            mock_pause.assert_called_once()

    @patch("entry_actions.pause")
    def test_does_nothing_when_event_list_is_empty(
        self,
        mock_pause
    ):
        original_content = (
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
                original_content,
                encoding="utf-8"
            )

            delete_event(
                original_content,
                [],
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

            mock_pause.assert_called_once()

class AddTaskTests(unittest.TestCase):

    @patch(
        "builtins.input",
        side_effect=["Buy seeds", ""]
    )
    def test_adds_task_before_notes_section(
        self,
        mock_input
    ):
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

            notes_start = original_content.find(
                "## Notes"
            )

            add_task(
                original_content,
                notes_start,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

    @patch(
        "builtins.input",
        side_effect=[
            "Buy seeds",
            "Test the pump",
            ""
        ]
    )
    def test_adds_multiple_tasks(
        self,
        mock_input
    ):
        original_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n"
            "- [ ] Buy seeds\n"
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

            notes_start = original_content.find(
                "## Notes"
            )

            add_task(
                original_content,
                notes_start,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_content
            )

    @patch("builtins.input", return_value="")
    def test_does_not_add_empty_task(
        self,
        mock_input
    ):
        original_content = (
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
                original_content,
                encoding="utf-8"
            )

            notes_start = original_content.find(
                "## Notes"
            )

            add_task(
                original_content,
                notes_start,
                journal_file
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                original_content
            )

class LineSelectionTests(unittest.TestCase):

    @patch("builtins.input", return_value="2")
    def test_selects_line_by_number(
        self,
        mock_input
    ):
        lines = [
            "- First note",
            "- Second note",
            "- Third note",
        ]

        result = select_line(
            lines,
            "Enter the line number: "
        )

        self.assertEqual(
            result,
            "- Second note"
        )

        mock_input.assert_called_once_with(
            "Enter the line number: "
        )

    @patch("builtins.input", return_value="abc")
    def test_returns_none_for_non_numeric_input(
        self,
        mock_input
    ):
        lines = [
            "- First note",
            "- Second note",
        ]

        result = select_line(
            lines,
            "Enter the line number: "
        )

        self.assertIsNone(result)

    @patch("builtins.input", return_value="3")
    def test_returns_none_for_number_outside_range(
        self,
        mock_input
    ):
        lines = [
            "- First note",
            "- Second note",
        ]

        result = select_line(
            lines,
            "Enter the line number: "
        )

        self.assertIsNone(result)

    @patch("builtins.input", return_value="0")
    def test_returns_none_for_zero(
        self,
        mock_input
    ):
        lines = [
            "- First note",
            "- Second note",
        ]

        result = select_line(
            lines,
            "Enter the line number: "
        )

        self.assertIsNone(result)

    def test_returns_none_when_line_list_is_empty(self):
        result = select_line(
            [],
            "Enter the line number: "
        )

        self.assertIsNone(result)

class PendingTaskListTests(unittest.TestCase):

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    def test_lists_pending_tasks_from_multiple_days(
        self,
        mock_stdout,
        mock_pause
    ):
        first_content = (
            "# Friday, 31 July 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n"
            "- [x] Test the pump\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        second_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Water plants\n"
            "- [-] Cancel order\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            first_file = journal_folder / "2026-07-31.md"
            second_file = journal_folder / "2026-08-01.md"

            first_file.write_text(
                first_content,
                encoding="utf-8"
            )

            second_file.write_text(
                second_content,
                encoding="utf-8"
            )

            list_pending_tasks(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "2026-07-31: - [ ] Buy seeds",
                output
            )

            self.assertIn(
                "2026-08-01: - [ ] Water plants",
                output
            )

            self.assertNotIn(
                "- [x] Test the pump",
                output
            )

            self.assertNotIn(
                "- [-] Cancel order",
                output
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    def test_reports_when_no_pending_tasks_exist(
        self,
        mock_stdout,
        mock_pause
    ):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n"
            "- [-] Cancel order\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            journal_file = journal_folder / "2026-08-01.md"

            journal_file.write_text(
                content,
                encoding="utf-8"
            )

            list_pending_tasks(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "No pending tasks found.",
                output
            )

            mock_pause.assert_called_once()

class JournalSearchTests(unittest.TestCase):

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="pump")
    def test_finds_text_across_journals(
        self,
        mock_input,
        mock_stdout,
        mock_pause
    ):
        first_content = (
            "# Friday, 31 July 2026\n\n"
            "## Tasks\n\n"
            "- [x] Test the pump\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        second_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- The pump worked correctly\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            first_file = journal_folder / "2026-07-31.md"
            second_file = journal_folder / "2026-08-01.md"

            first_file.write_text(
                first_content,
                encoding="utf-8"
            )

            second_file.write_text(
                second_content,
                encoding="utf-8"
            )

            search_journals(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "2026-07-31",
                output
            )

            self.assertIn(
                "- [x] Test the pump",
                output
            )

            self.assertIn(
                "2026-08-01",
                output
            )

            self.assertIn(
                "- The pump worked correctly",
                output
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="GREENHOUSE")
    def test_search_is_case_insensitive(
        self,
        mock_input,
        mock_stdout,
        mock_pause
    ):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "- Greenhouse temperature was high\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            journal_file = journal_folder / "2026-08-01.md"

            journal_file.write_text(
                content,
                encoding="utf-8"
            )

            search_journals(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "Greenhouse temperature was high",
                output
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="solar panel")
    def test_reports_when_no_matches_are_found(
        self,
        mock_input,
        mock_stdout,
        mock_pause
    ):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            journal_file = journal_folder / "2026-08-01.md"

            journal_file.write_text(
                content,
                encoding="utf-8"
            )

            search_journals(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "No matches found.",
                output
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="")
    def test_rejects_empty_search_text(
        self,
        mock_input,
        mock_stdout,
        mock_pause
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            search_journals(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "No search text entered.",
                output
            )

            mock_pause.assert_called_once()

class JournalListingTests(unittest.TestCase):

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    def test_lists_journals_in_date_order(
        self,
        mock_stdout,
        mock_pause
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            first_file = journal_folder / "2026-07-31.md"
            second_file = journal_folder / "2026-08-01.md"

            first_file.write_text(
                "First journal",
                encoding="utf-8"
            )

            second_file.write_text(
                "Second journal",
                encoding="utf-8"
            )

            list_journals(journal_folder)

            output = mock_stdout.getvalue()

            first_position = output.find("2026-07-31")
            second_position = output.find("2026-08-01")

            self.assertNotEqual(first_position, -1)
            self.assertNotEqual(second_position, -1)

            self.assertLess(
                first_position,
                second_position
            )

            self.assertIn(
                "Friday, 31 July 2026",
                output
            )

            self.assertIn(
                "Saturday, 01 August 2026",
                output
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    def test_reports_when_no_journals_exist(
        self,
        mock_stdout,
        mock_pause
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            list_journals(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "No journal files found.",
                output
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    def test_ignores_markdown_files_without_date_names(
        self,
        mock_stdout,
        mock_pause
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            valid_file = journal_folder / "2026-08-01.md"
            invalid_file = journal_folder / "notes.md"

            valid_file.write_text(
                "Valid journal",
                encoding="utf-8"
            )

            invalid_file.write_text(
                "Not a dated journal",
                encoding="utf-8"
            )

            list_journals(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "2026-08-01",
                output
            )

            self.assertNotIn(
                "notes.md",
                output
            )

            mock_pause.assert_called_once()

class ViewJournalTests(unittest.TestCase):

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="2026-08-01")
    def test_displays_selected_journal(
        self,
        mock_input,
        mock_stdout,
        mock_pause
    ):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)
            journal_file = journal_folder / "2026-08-01.md"

            journal_file.write_text(
                content,
                encoding="utf-8"
            )

            view_journal(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "# Saturday, 01 August 2026",
                output
            )

            self.assertIn(
                "- [ ] Buy seeds",
                output
            )

            mock_input.assert_called_once_with(
                "Enter the date to view (YYYY-MM-DD): "
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="2026-08-02")
    def test_reports_when_journal_does_not_exist(
        self,
        mock_input,
        mock_stdout,
        mock_pause
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            view_journal(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "No journal exists for 2026-08-02.",
                output
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    @patch("sys.stdout", new_callable=StringIO)
    @patch("builtins.input", return_value="not-a-date")
    def test_rejects_invalid_date(
        self,
        mock_input,
        mock_stdout,
        mock_pause
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            view_journal(journal_folder)

            output = mock_stdout.getvalue()

            self.assertIn(
                "Please enter a valid date in YYYY-MM-DD format.",
                output
            )

            mock_pause.assert_called_once()

class PreviousDayReviewTests(unittest.TestCase):

    @patch("journal_actions.pause")
    @patch(
        "builtins.input",
        side_effect=["1", "1"]
    )
    def test_migrates_pending_task_from_previous_day(
        self,
        mock_input,
        mock_pause
    ):
        today = date(2026, 8, 1)

        previous_content = (
            "# Friday, 31 July 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n"
            "- [x] Test the pump\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        today_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_previous_content = (
            "# Friday, 31 July 2026\n\n"
            "## Tasks\n\n"
            "- [>] Buy seeds\n"
            "- [x] Test the pump\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        expected_today_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            previous_file = (
                journal_folder
                / "2026-07-31.md"
            )

            journal_file = (
                journal_folder
                / "2026-08-01.md"
            )

            previous_file.write_text(
                previous_content,
                encoding="utf-8"
            )

            journal_file.write_text(
                today_content,
                encoding="utf-8"
            )

            review_previous_day(
                journal_folder,
                journal_file,
                today
            )

            self.assertEqual(
                previous_file.read_text(encoding="utf-8"),
                expected_previous_content
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                expected_today_content
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    @patch("builtins.input", return_value="2")
    def test_returns_without_migrating_task(
        self,
        mock_input,
        mock_pause
    ):
        today = date(2026, 8, 1)

        previous_content = (
            "# Friday, 31 July 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        today_content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            previous_file = (
                journal_folder
                / "2026-07-31.md"
            )

            journal_file = (
                journal_folder
                / "2026-08-01.md"
            )

            previous_file.write_text(
                previous_content,
                encoding="utf-8"
            )

            journal_file.write_text(
                today_content,
                encoding="utf-8"
            )

            review_previous_day(
                journal_folder,
                journal_file,
                today
            )

            self.assertEqual(
                previous_file.read_text(encoding="utf-8"),
                previous_content
            )

            self.assertEqual(
                journal_file.read_text(encoding="utf-8"),
                today_content
            )

            mock_pause.assert_not_called()

    @patch("journal_actions.pause") 
    def test_reports_when_previous_journal_is_missing(
        self,
        mock_pause
    ):
        today = date(2026, 8, 1)

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            journal_file = (
                journal_folder
                / "2026-08-01.md"
            )

            journal_file.write_text(
                (
                    "# Saturday, 01 August 2026\n\n"
                    "## Tasks\n\n"
                    "## Notes\n\n"
                    "## Events\n"
                ),
                encoding="utf-8"
            )

            review_previous_day(
                journal_folder,
                journal_file,
                today
            )

            mock_pause.assert_called_once()

    @patch("journal_actions.pause")
    def test_reports_when_previous_day_has_no_pending_tasks(
        self,
        mock_pause
    ):
        today = date(2026, 8, 1)

        previous_content = (
            "# Friday, 31 July 2026\n\n"
            "## Tasks\n\n"
            "- [x] Buy seeds\n"
            "- [-] Cancel order\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            journal_folder = Path(temporary_directory)

            previous_file = (
                journal_folder
                / "2026-07-31.md"
            )

            journal_file = (
                journal_folder
                / "2026-08-01.md"
            )

            previous_file.write_text(
                previous_content,
                encoding="utf-8"
            )

            journal_file.write_text(
                (
                    "# Saturday, 01 August 2026\n\n"
                    "## Tasks\n\n"
                    "## Notes\n\n"
                    "## Events\n"
                ),
                encoding="utf-8"
            )

            review_previous_day(
                journal_folder,
                journal_file,
                today
            )

            mock_pause.assert_called_once()

if __name__ == "__main__":
    unittest.main()