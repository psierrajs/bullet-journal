import tempfile
import unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch
from pathlib import Path


from main import (
    add_event,
    add_note,
    add_task,
    append_line,
    cancel_task,
    complete_task,
    create_daily_journal,
    delete_event,
    delete_note,
    delete_task,
    edit_event,
    edit_note,
    edit_task,
    get_section_lines,
    get_section_positions,
    get_task_lines,
    insert_before_section,
    migrate_task,
    reopen_task,
    replace_task,
    restore_backup,
    select_line,
    select_task,
    validate_journal_content,
    write_journal,
)

class JournalValidationTests(unittest.TestCase):

    def test_valid_journal_structure(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        result = validate_journal_content(content)

        self.assertTrue(result)

    def test_missing_tasks_section(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        result = validate_journal_content(content)

        self.assertFalse(result)

    def test_missing_notes_section(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Events\n"
        )

        result = validate_journal_content(content)

        self.assertFalse(result)

    def test_missing_events_section(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n"
        )

        result = validate_journal_content(content)

        self.assertFalse(result)

    def test_sections_in_wrong_order(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Notes\n\n"
            "## Tasks\n\n"
            "## Events\n"
        )

        result = validate_journal_content(content)

        self.assertFalse(result)

class TaskParsingTests(unittest.TestCase):

    def test_returns_all_task_lines(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n"
            "- [x] Test the pump\n"
            "- [-] Cancel old order\n"
            "- [>] Move task forward\n\n"
            "## Notes\n\n"
            "- Greenhouse temperature was high\n\n"
            "## Events\n"
        )

        result = get_task_lines(content)

        expected = [
            "- [ ] Buy seeds",
            "- [x] Test the pump",
            "- [-] Cancel old order",
            "- [>] Move task forward",
        ]

        self.assertEqual(result, expected)

    def test_returns_empty_list_when_tasks_section_is_empty(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        result = get_task_lines(content)

        self.assertEqual(result, [])

    def test_ignores_non_task_lines(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "This is not a task\n"
            "- Ordinary bullet\n"
            "- [ ] Real task\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        result = get_task_lines(content)

        self.assertEqual(
            result,
            ["- [ ] Real task"]
        )

    def test_returns_none_when_tasks_section_is_missing(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        result = get_task_lines(content)

        self.assertIsNone(result)

    def test_returns_none_when_notes_section_is_missing(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Events\n"
        )

        result = get_task_lines(content)

        self.assertIsNone(result)

class SectionPositionTests(unittest.TestCase):

    def test_returns_section_positions(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "- Check water level\n\n"
            "## Events\n\n"
            "- 18:00 Meeting\n"
        )

        result = get_section_positions(content)

        expected = (
            content.find("## Tasks\n"),
            content.find("## Notes"),
            content.find("## Events"),
        )

        self.assertEqual(result, expected)

    def test_returns_none_when_tasks_section_is_missing(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Notes\n\n"
            "## Events\n"
        )

        result = get_section_positions(content)

        self.assertIsNone(result)

    def test_returns_none_when_notes_section_is_missing(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Events\n"
        )

        result = get_section_positions(content)

        self.assertIsNone(result)

    def test_returns_none_when_events_section_is_missing(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n"
        )

        result = get_section_positions(content)

        self.assertIsNone(result)

class SectionLineTests(unittest.TestCase):

    def test_returns_lines_between_two_sections(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "- [ ] Buy seeds\n\n"
            "## Notes\n\n"
            "- Check water level\n"
            "- Greenhouse was warm\n\n"
            "## Events\n\n"
            "- 18:00 Meeting\n"
        )

        notes_start = content.find("## Notes")
        events_start = content.find("## Events")

        result = get_section_lines(
            content,
            notes_start,
            events_start
        )

        expected = [
            "- Check water level",
            "- Greenhouse was warm",
        ]

        self.assertEqual(result, expected)

    def test_returns_lines_until_end_of_file(self):
        content = (
            "# Saturday, 01 August 2026\n\n"
            "## Tasks\n\n"
            "## Notes\n\n"
            "## Events\n\n"
            "- 18:00 Meeting\n"
            "- 20:00 Water plants\n"
        )

        events_start = content.find("## Events")

        result = get_section_lines(
            content,
            events_start
        )

        expected = [
            "- 18:00 Meeting",
            "- 20:00 Water plants",
        ]

        self.assertEqual(result, expected)

    def test_ignores_blank_lines(self):
        content = (
            "## Notes\n\n"
            "- First note\n\n"
            "\n"
            "- Second note\n"
            "## Events\n"
        )

        notes_start = content.find("## Notes")
        events_start = content.find("## Events")

        result = get_section_lines(
            content,
            notes_start,
            events_start
        )

        self.assertEqual(
            result,
            [
                "- First note",
                "- Second note",
            ]
        )

    def test_returns_empty_list_for_empty_section(self):
        content = (
            "## Notes\n\n"
            "## Events\n"
        )

        notes_start = content.find("## Notes")
        events_start = content.find("## Events")

        result = get_section_lines(
            content,
            notes_start,
            events_start
        )

        self.assertEqual(result, [])    

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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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
    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

    @patch("main.pause")
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

if __name__ == "__main__":
    unittest.main()