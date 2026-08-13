import os
import unittest
from pathlib import Path
from unittest.mock import patch

from bullet_journal.paths import (
    get_app_data_directory,
    get_journal_directory,
    open_journal_directory,
)


class AppDataDirectoryTests(unittest.TestCase):
    @patch("bullet_journal.paths.Path.home")
    @patch("bullet_journal.paths.sys.platform", "darwin")
    def test_macos_app_data_directory(self, mock_home):
        mock_home.return_value = Path("/Users/testuser")

        result = get_app_data_directory()

        self.assertEqual(
            result,
            Path(
                "/Users/testuser/Library/"
                "Application Support/BulletJournal"
            ),
        )

    @patch.dict(
        os.environ,
        {"APPDATA": r"C:\Users\Test\AppData\Roaming"},
        clear=True,
    )
    @patch("bullet_journal.paths.sys.platform", "win32")
    def test_windows_app_data_directory(self):
        result = get_app_data_directory()

        self.assertEqual(
            result,
            Path(
                r"C:\Users\Test\AppData\Roaming"
            )
            / "BulletJournal",
        )

    @patch.dict(
        os.environ,
        {"XDG_DATA_HOME": "/home/test/.data"},
        clear=True,
    )
    @patch("bullet_journal.paths.sys.platform", "linux")
    def test_linux_xdg_app_data_directory(self):
        result = get_app_data_directory()

        self.assertEqual(
            result,
            Path("/home/test/.data/BulletJournal"),
        )

    @patch.dict(
        os.environ,
        {},
        clear=True,
    )
    @patch("bullet_journal.paths.Path.home")
    @patch("bullet_journal.paths.sys.platform", "linux")
    def test_linux_default_app_data_directory(
        self,
        mock_home,
    ):
        mock_home.return_value = Path("/home/test")

        result = get_app_data_directory()

        self.assertEqual(
            result,
            Path(
                "/home/test/.local/share/BulletJournal"
            ),
        )

    @patch(
        "bullet_journal.paths.get_app_data_directory"
    )
    def test_journal_directory_is_inside_app_data(
        self,
        mock_app_data,
    ):
        mock_app_data.return_value = Path("/tmp/BulletJournal")

        result = get_journal_directory()

        self.assertEqual(
            result,
            Path("/tmp/BulletJournal/journal"),
        )

    @patch("bullet_journal.paths.subprocess.run")
    @patch(
        "bullet_journal.paths.get_journal_directory"
    )
    @patch(
        "bullet_journal.paths.sys.platform",
        "darwin",
    )
    def test_open_journal_directory_on_macos(
        self,
        mock_journal_directory,
        mock_run,
    ):
        journal_directory = Path(
            "/tmp/BulletJournal-test-macos"
        )
        mock_journal_directory.return_value = (
            journal_directory
        )

        open_journal_directory()

        self.assertTrue(
            journal_directory.exists()
        )
        mock_run.assert_called_once_with(
            ["open", journal_directory],
            check=False,
        )

        journal_directory.rmdir()

    @patch(
        "bullet_journal.paths.os.startfile",
        create=True,
    )
    @patch(
        "bullet_journal.paths.get_journal_directory"
    )
    @patch(
        "bullet_journal.paths.sys.platform",
        "win32",
    )
    def test_open_journal_directory_on_windows(
        self,
        mock_journal_directory,
        mock_startfile,
    ):
        journal_directory = Path(
            "/tmp/BulletJournal-test-windows"
        )
        mock_journal_directory.return_value = (
            journal_directory
        )

        open_journal_directory()

        self.assertTrue(
            journal_directory.exists()
        )
        mock_startfile.assert_called_once_with(
            journal_directory
        )

        journal_directory.rmdir()

    @patch("bullet_journal.paths.subprocess.run")
    @patch(
        "bullet_journal.paths.get_journal_directory"
    )
    @patch(
        "bullet_journal.paths.sys.platform",
        "linux",
    )
    def test_open_journal_directory_on_linux(
        self,
        mock_journal_directory,
        mock_run,
    ):
        journal_directory = Path(
            "/tmp/BulletJournal-test-linux"
        )
        mock_journal_directory.return_value = (
            journal_directory
        )

        open_journal_directory()

        self.assertTrue(
            journal_directory.exists()
        )
        mock_run.assert_called_once_with(
            ["xdg-open", journal_directory],
            check=False,
        )

        journal_directory.rmdir()

if __name__ == "__main__":
    unittest.main()