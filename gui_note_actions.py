from datetime import date
from tkinter import messagebox, simpledialog, ttk

from gui_helpers import refresh_journal_status
from bullet_journal.journal_parser import (
    get_section_lines,
    get_section_positions,
)
from journal_storage import (
    create_daily_journal,
    insert_before_section,
    write_journal,
)


def refresh_notes(
    journal_file,
    note_frame,
    selected_note_var,
):
    content = journal_file.read_text(
        encoding="utf-8"
    )

    positions = get_section_positions(content)

    if positions is None:
        raise ValueError(
            "Invalid journal structure."
        )

    _, notes_start, events_start = positions

    notes = get_section_lines(
        content,
        notes_start,
        events_start,
    )

    selected_note_var.set("")

    fill_note_section(
        note_frame,
        notes,
        selected_note_var,
    )


def fill_note_section(
    frame,
    note_lines,
    selected_note_var,
):
    for widget in frame.winfo_children():
        widget.destroy()

    if not note_lines:
        from tkinter import ttk

        ttk.Label(
            frame,
            text="No notes yet.",
        ).pack(anchor="w")
        return

    from tkinter import ttk

    for note_line in note_lines:
        ttk.Radiobutton(
            frame,
            text=note_line,
            variable=selected_note_var,
            value=note_line,
        ).pack(
            anchor="w",
            pady=2,
        )


def add_note_gui(
    root,
    journal_file,
    note_frame,
    selected_note_var,
):
    note_text = simpledialog.askstring(
        "Add note",
        "Note:",
        parent=root,
    )

    if not note_text:
        return

    if not journal_file.exists():
        from datetime import date

        journal_date = date.fromisoformat(
            journal_file.stem
        )

        create_daily_journal(
            journal_file,
            journal_date,
        )

    content = journal_file.read_text(
        encoding="utf-8"
    )

    section_positions = get_section_positions(
        content
    )

    if section_positions is None:
        raise ValueError(
            "Invalid journal structure."
        )

    _, _, events_start = section_positions

    insert_before_section(
        content,
        events_start,
        f"- {note_text}",
        journal_file,
    )

    refresh_notes(
        journal_file,
        note_frame,
        selected_note_var,
    )

    refresh_journal_status(
        journal_file,
        note_frame,
    )


def edit_note_gui(
    root,
    journal_file,
    note_frame,
    selected_note_var,
):
    selected_note = selected_note_var.get()

    if not selected_note:
        return

    current_text = selected_note.removeprefix(
        "- "
    )

    new_text = simpledialog.askstring(
        "Edit note",
        "Note:",
        initialvalue=current_text,
        parent=root,
    )

    if not new_text:
        return

    edited_note = f"- {new_text}"

    content = journal_file.read_text(
        encoding="utf-8"
    )

    new_content = content.replace(
        selected_note,
        edited_note,
        1,
    )

    write_journal(
        journal_file,
        new_content,
    )

    refresh_notes(
        journal_file,
        note_frame,
        selected_note_var,
    )


def delete_note_gui(
    root,
    journal_file,
    note_frame,
    selected_note_var,
):
    selected_note = selected_note_var.get()

    if not selected_note:
        return

    confirmed = messagebox.askyesno(
        "Delete note",
        (
            "Delete this note?"
            f"\n\n{selected_note}"
        ),
        parent=root,
    )

    if not confirmed:
        return

    content = journal_file.read_text(
        encoding="utf-8"
    )

    new_content = content.replace(
        selected_note + "\n",
        "",
        1,
    )

    if new_content == content:
        new_content = content.replace(
            selected_note,
            "",
            1,
        )

    write_journal(
        journal_file,
        new_content,
    )

    refresh_notes(
        journal_file,
        note_frame,
        selected_note_var,
    )

    