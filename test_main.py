import unittest

from main import validate_journal_content
from main import get_task_lines, validate_journal_content


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


if __name__ == "__main__":
    unittest.main()