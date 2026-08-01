import unittest
from io import StringIO
from unittest.mock import patch

from terminal_ui import (
    display_journal_details,
    display_menu,
    display_tasks,
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

if __name__ == "__main__":
    unittest.main()