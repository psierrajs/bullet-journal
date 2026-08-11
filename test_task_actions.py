import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from bullet_journal.task_actions import (
    add_task,
    cancel_task,
    complete_task,
    delete_task,
    edit_task,
    migrate_task,
    reopen_task,
)

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

class CancelTaskTests(unittest.TestCase):

    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

class CompleteTaskTests(unittest.TestCase):

    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

class DeleteTaskTests(unittest.TestCase):

    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

class EditTaskTests(unittest.TestCase):

    @patch("bullet_journal.task_actions.pause")
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
    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

class MigrateTaskTests(unittest.TestCase):

    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

class ReopenTaskTests(unittest.TestCase):

    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

    @patch("bullet_journal.task_actions.pause")
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

if __name__ == "__main__":
    unittest.main()