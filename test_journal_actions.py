import tempfile
import unittest
from datetime import date
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from journal_actions import (
    list_journals,
    list_pending_tasks,
    review_previous_day,
    search_journals,
    view_journal,
)

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


