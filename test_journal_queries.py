import tempfile
import unittest
from datetime import date
from pathlib import Path

from bullet_journal.journal_queries import (
    get_journal_dates,
    get_pending_tasks,
    search_journal_files,
)


class TestJournalQueries(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.journal_folder = Path(
            self.temp_dir.name
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_journal(
        self,
        filename,
        content,
    ):
        journal_file = (
            self.journal_folder
            / filename
        )

        journal_file.write_text(
            content,
            encoding="utf-8",
        )

        return journal_file

    def test_search_journal_files_finds_match(self):
        self.create_journal(
            "2026-08-01.md",
            (
                "# Friday, 01 August 2026\n\n"
                "## Tasks\n\n"
                "- [ ] Finish report\n\n"
                "## Notes\n\n"
                "## Events\n"
            ),
        )

        results = search_journal_files(
            self.journal_folder,
            "report",
        )

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0][0],
            "2026-08-01",
        )

        self.assertEqual(
            results[0][2],
            "- [ ] Finish report",
        )

    def test_search_is_case_insensitive(self):
        self.create_journal(
            "2026-08-02.md",
            (
                "# Saturday, 02 August 2026\n\n"
                "## Tasks\n\n"
                "- [ ] Review REPORT\n\n"
                "## Notes\n\n"
                "## Events\n"
            ),
        )

        results = search_journal_files(
            self.journal_folder,
            "report",
        )

        self.assertEqual(
            len(results),
            1,
        )

    def test_search_returns_multiple_matches(self):
        self.create_journal(
            "2026-08-03.md",
            (
                "# Sunday, 03 August 2026\n\n"
                "## Tasks\n\n"
                "- [ ] Finish report\n\n"
                "## Notes\n\n"
                "- Report meeting tomorrow\n\n"
                "## Events\n"
            ),
        )

        results = search_journal_files(
            self.journal_folder,
            "report",
        )

        self.assertEqual(
            len(results),
            2,
        )

    def test_search_returns_empty_list_when_no_match(self):
        self.create_journal(
            "2026-08-04.md",
            (
                "# Monday, 04 August 2026\n\n"
                "## Tasks\n\n"
                "- [ ] Buy groceries\n\n"
                "## Notes\n\n"
                "## Events\n"
            ),
        )

        results = search_journal_files(
            self.journal_folder,
            "report",
        )

        self.assertEqual(
            results,
            [],
        )

    def test_get_pending_tasks_finds_open_tasks(self):
        self.create_journal(
            "2026-08-05.md",
            (
                "# Tuesday, 05 August 2026\n\n"
                "## Tasks\n\n"
                "- [ ] Open task\n"
                "- [x] Completed task\n"
                "- [-] Cancelled task\n"
                "- [>] Migrated task\n\n"
                "## Notes\n\n"
                "## Events\n"
            ),
        )

        pending_tasks = get_pending_tasks(
            self.journal_folder
        )

        self.assertEqual(
            pending_tasks,
            [
                (
                    "2026-08-05",
                    "- [ ] Open task",
                )
            ],
        )

    def test_get_pending_tasks_across_multiple_journals(self):
        self.create_journal(
            "2026-08-06.md",
            (
                "# Wednesday, 06 August 2026\n\n"
                "## Tasks\n\n"
                "- [ ] First task\n\n"
                "## Notes\n\n"
                "## Events\n"
            ),
        )

        self.create_journal(
            "2026-08-07.md",
            (
                "# Thursday, 07 August 2026\n\n"
                "## Tasks\n\n"
                "- [ ] Second task\n\n"
                "## Notes\n\n"
                "## Events\n"
            ),
        )

        pending_tasks = get_pending_tasks(
            self.journal_folder
        )

        self.assertEqual(
            pending_tasks,
            [
                (
                    "2026-08-06",
                    "- [ ] First task",
                ),
                (
                    "2026-08-07",
                    "- [ ] Second task",
                ),
            ],
        )

    def test_get_pending_tasks_returns_empty_list(self):
        self.create_journal(
            "2026-08-08.md",
            (
                "# Friday, 08 August 2026\n\n"
                "## Tasks\n\n"
                "- [x] Completed task\n\n"
                "## Notes\n\n"
                "## Events\n"
            ),
        )

        pending_tasks = get_pending_tasks(
            self.journal_folder
        )

        self.assertEqual(
            pending_tasks,
            [],
        )
    def test_get_journal_dates_returns_valid_dates_only(self):
        self.create_journal(
            "2026-08-01.md",
            (
                "# Friday, 01 August 2026\n\n"
                "## Tasks\n\n"
                "## Notes\n\n"
                "## Events\n"
            ),
        )

        self.create_journal(
            "2026-08-03.md",
            (
                "# Sunday, 03 August 2026\n\n"
                "## Tasks\n\n"
                "## Notes\n\n"
                "## Events\n"
            ),
        )

        self.create_journal(
            "not-a-date.md",
            "Ignore this file.",
        )

        journal_dates = get_journal_dates(
            self.journal_folder
        )

        self.assertEqual(
            journal_dates,
            [
                date(2026, 8, 1),
                date(2026, 8, 3),
            ],
        )


if __name__ == "__main__":
    unittest.main()