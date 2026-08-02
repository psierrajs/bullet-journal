import unittest
from io import StringIO
from unittest.mock import patch
from io import StringIO

from terminal_ui import (
    build_progress_bar,
    display_journal_details,
    display_menu,
    display_tasks,
    display_task_summary,
    pause,
    select_line,
    select_task,
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

class TaskSummaryDisplayTests(unittest.TestCase):

    @patch("sys.stdout", new_callable=StringIO)
    def test_displays_task_counts(self, mock_stdout):
        content = """# Sunday, 02 August 2026

## Tasks

- [ ] Buy seeds
- [ ] Check water level
- [x] Test the pump
- [-] Repair old hose
- [>] Order compost

## Notes

## Events
"""

        display_task_summary(content)

        output = mock_stdout.getvalue()

        self.assertIn("Task summary:", output)
        self.assertIn("Total: 5", output)
        self.assertIn("Open: 2", output)
        self.assertIn("Completed: 1", output)
        self.assertIn("Cancelled: 1", output)
        self.assertIn("Migrated: 1", output)
        self.assertIn("Progress: [###-------] 33%", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_displays_zero_counts_when_no_tasks_exist(self, mock_stdout):
        content = """# Sunday, 02 August 2026

## Tasks

## Notes

## Events
"""

        display_task_summary(content)

        output = mock_stdout.getvalue()

        self.assertIn("Open: 0", output)
        self.assertIn("Completed: 0", output)
        self.assertIn("Cancelled: 0", output)
        self.assertIn("Migrated: 0", output)
        self.assertIn("Progress: [----------] 0%", output)

class JournalDetailsDisplayTests(unittest.TestCase):

    @patch("sys.stdout", new_callable=StringIO)
    def test_displays_summary_notes_and_events(self, mock_stdout):
        journal_content = """# Sunday, 02 August 2026

## Tasks

- [ ] Buy seeds
- [x] Test the pump

## Notes

- Greenhouse was warm

## Events

- 18:00 Meeting
"""

        display_journal_details(
            ["- Greenhouse was warm"],
            ["- 18:00 Meeting"],
            journal_content
        )

        output = mock_stdout.getvalue()

        self.assertIn("Task summary:", output)
        self.assertIn("Open: 1", output)
        self.assertIn("Completed: 1", output)
        self.assertIn("Today's notes:", output)
        self.assertIn("- Greenhouse was warm", output)
        self.assertIn("Today's events:", output)
        self.assertIn("- 18:00 Meeting", output)
        self.assertIn("Progress: [#####-----] 50%", output)

class ProgressBarTests(unittest.TestCase):

    def test_builds_empty_progress_bar(self):
        result = build_progress_bar(0)

        self.assertEqual(result, "[----------]")

    def test_builds_half_complete_progress_bar(self):
        result = build_progress_bar(50)

        self.assertEqual(result, "[#####-----]")

    def test_builds_complete_progress_bar(self):
        result = build_progress_bar(100)

        self.assertEqual(result, "[##########]")

if __name__ == "__main__":
    unittest.main()