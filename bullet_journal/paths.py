import os
import sys
import subprocess
from pathlib import Path


def get_app_data_directory():
    if sys.platform == "darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "BulletJournal"
        )

    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")

        if appdata:
            return Path(appdata) / "BulletJournal"

        return Path.home() / "AppData" / "Roaming" / "BulletJournal"

    xdg_data_home = os.environ.get("XDG_DATA_HOME")

    if xdg_data_home:
        return Path(xdg_data_home) / "BulletJournal"

    return (
        Path.home()
        / ".local"
        / "share"
        / "BulletJournal"
    )


def get_journal_directory():
    return get_app_data_directory() / "journal"

def open_journal_directory():
    journal_directory = get_journal_directory()
    journal_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    if sys.platform == "darwin":
        subprocess.run(
            ["open", journal_directory],
            check=False,
        )
        return

    if sys.platform == "win32":
        os.startfile(journal_directory)
        return

    subprocess.run(
        ["xdg-open", journal_directory],
        check=False,
    )

def open_path(path):
    path = Path(path)

    if sys.platform == "darwin":
        subprocess.run(
            ["open", path],
            check=False,
        )
        return

    if sys.platform == "win32":
        os.startfile(path)
        return

    subprocess.run(
        ["xdg-open", path],
        check=False,
    )