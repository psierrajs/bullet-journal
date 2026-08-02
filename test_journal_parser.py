import unittest

from journal_parser import (
    get_section_lines,
    get_section_positions,
    get_task_lines,
    validate_journal_content,
    count_tasks_by_status,
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

class TaskStatusCountTests(unittest.TestCase):

    def test_counts_tasks_by_status(self):
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

        result = count_tasks_by_status(content)

        self.assertEqual(
            result,
            {
                "open": 2,
                "completed": 1,
                "cancelled": 1,
                "migrated": 1,
            },
        )

    def test_returns_zero_counts_when_no_tasks_exist(self):
        content = """# Sunday, 02 August 2026

## Tasks

## Notes

## Events
"""

        result = count_tasks_by_status(content)

        self.assertEqual(
            result,
            {
                "open": 0,
                "completed": 0,
                "cancelled": 0,
                "migrated": 0,
            },
        )


if __name__ == "__main__":
    main()
