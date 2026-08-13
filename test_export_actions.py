import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from bullet_journal.export_actions import export_journals


class ExportJournalsTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_directory.name)

        self.journal_directory = (
            self.base_path / "journal"
        )
        self.journal_directory.mkdir()

        self.destination_file = (
            self.base_path / "journals.zip"
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_exports_markdown_journals_to_zip(self):
        first_journal = (
            self.journal_directory / "2026-08-12.md"
        )
        second_journal = (
            self.journal_directory / "2026-08-13.md"
        )

        first_journal.write_text(
            "# First journal\n",
            encoding="utf-8",
        )
        second_journal.write_text(
            "# Second journal\n",
            encoding="utf-8",
        )

        result = export_journals(
            self.journal_directory,
            self.destination_file,
        )

        self.assertTrue(result)
        self.assertTrue(
            self.destination_file.exists()
        )

        with ZipFile(self.destination_file) as archive:
            self.assertEqual(
                sorted(archive.namelist()),
                [
                    "2026-08-12.md",
                    "2026-08-13.md",
                ],
            )

    def test_ignores_non_markdown_files(self):
        journal_file = (
            self.journal_directory / "2026-08-13.md"
        )
        other_file = (
            self.journal_directory / "notes.txt"
        )

        journal_file.write_text(
            "# Journal\n",
            encoding="utf-8",
        )
        other_file.write_text(
            "Do not export",
            encoding="utf-8",
        )

        export_journals(
            self.journal_directory,
            self.destination_file,
        )

        with ZipFile(self.destination_file) as archive:
            self.assertEqual(
                archive.namelist(),
                ["2026-08-13.md"],
            )

    def test_returns_false_when_no_journals_exist(self):
        result = export_journals(
            self.journal_directory,
            self.destination_file,
        )

        self.assertFalse(result)
        self.assertFalse(
            self.destination_file.exists()
        )


if __name__ == "__main__":
    unittest.main()