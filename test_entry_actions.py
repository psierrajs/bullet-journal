import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from bullet_journal.entry_actions import (
    add_event,
    add_note,
    delete_event,
    delete_note,
    edit_event,
    edit_note,
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

class DeleteEventTests(unittest.TestCase):

    @patch("bullet_journal.entry_actions.pause")
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

    @patch("bullet_journal.entry_actions.pause")
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

    @patch("bullet_journal.entry_actions.pause")
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

class DeleteNoteTests(unittest.TestCase):

    @patch("bullet_journal.entry_actions.pause")
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

    @patch("bullet_journal.entry_actions.pause")
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

    @patch("bullet_journal.entry_actions.pause")
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

    @patch("bullet_journal.entry_actions.pause")
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

    @patch("bullet_journal.entry_actions.pause")
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

    @patch("bullet_journal.entry_actions.pause")
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

class EditNoteTests(unittest.TestCase):

    @patch("bullet_journal.entry_actions.pause")
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

    @patch("bullet_journal.entry_actions.pause")
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

if __name__ == "__main__":
    unittest.main()
