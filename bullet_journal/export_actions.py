from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def export_journals(journal_directory, destination_file):
    journal_files = sorted(
        journal_directory.glob("*.md")
    )

    if not journal_files:
        return False

    destination_file = Path(destination_file)

    with ZipFile(
        destination_file,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        for journal_file in journal_files:
            archive.write(
                journal_file,
                arcname=journal_file.name,
            )

    return True