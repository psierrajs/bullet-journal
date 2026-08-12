import os
import sys
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