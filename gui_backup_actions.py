from datetime import date
from tkinter import messagebox

from bullet_journal.journal_storage import write_journal


def restore_backup_gui(
    root,
    journal_file,
    load_date_callback,
):
    backup_file = journal_file.with_suffix(
        journal_file.suffix + ".bak"
    )

    if not backup_file.exists():
        messagebox.showinfo(
            "Restore backup",
            "No backup exists for this journal.",
            parent=root,
        )
        return

    confirmed = messagebox.askyesno(
        "Restore backup",
        (
            f"Restore backup for "
            f"{journal_file.stem}?\n\n"
            "The current journal will be replaced."
        ),
        parent=root,
    )

    if not confirmed:
        return

    backup_content = backup_file.read_text(
        encoding="utf-8"
    )

    write_journal(
        journal_file,
        backup_content,
    )

    journal_date = date.fromisoformat(
        journal_file.stem
    )

    load_date_callback(
        journal_date
    )

    messagebox.showinfo(
        "Restore backup",
        "Backup restored successfully.",
        parent=root,
    )

    