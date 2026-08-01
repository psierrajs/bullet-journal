import unittest

from main import validate_journal_content


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


if __name__ == "__main__":
    unittest.main()