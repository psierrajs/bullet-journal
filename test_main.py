from pathlib import Path
import tempfile
import unittest

from main import (
    get_section_lines,
    get_section_positions,
    get_task_lines,
    replace_task,
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

if __name__ == "__main__":
    unittest.main()