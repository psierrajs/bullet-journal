from datetime import date
from tkinter import messagebox, simpledialog, ttk

from .gui_helpers import refresh_journal_status
from .journal_parser import (
    get_section_lines,
    get_section_positions,
)
from .journal_storage import (
    create_daily_journal,
    write_journal,
)


def fill_event_section(
    frame,
    event_lines,
    selected_event_var,
):
    for widget in frame.winfo_children():
        widget.destroy()

    if not event_lines:
        ttk.Label(
            frame,
            text="No events yet.",
        ).pack(anchor="w")
        return

    for event_line in event_lines:
        ttk.Radiobutton(
            frame,
            text=event_line,
            variable=selected_event_var,
            value=event_line,
        ).pack(
            anchor="w",
            pady=2,
        )


def refresh_events(
    journal_file,
    event_frame,
    selected_event_var,
):
    content = journal_file.read_text(
        encoding="utf-8"
    )

    positions = get_section_positions(content)

    if positions is None:
        raise ValueError(
            "Invalid journal structure."
        )

    _, _, events_start = positions

    events = get_section_lines(
        content,
        events_start,
    )

    selected_event_var.set("")

    fill_event_section(
        event_frame,
        events,
        selected_event_var,
    )


def add_event_gui(
    root,
    journal_file,
    event_frame,
    selected_event_var,
):
    event_text = simpledialog.askstring(
        "Add event",
        "Event:",
        parent=root,
    )

    if not event_text:
        return

    if not journal_file.exists():
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

    new_content = (
        content.rstrip()
        + f"\n- {event_text}\n"
    )

    write_journal(
        journal_file,
        new_content,
    )

    refresh_events(
        journal_file,
        event_frame,
        selected_event_var,
    )

    refresh_journal_status(
        journal_file,
        event_frame,
    )


def edit_event_gui(
    root,
    journal_file,
    event_frame,
    selected_event_var,
):
    selected_event = selected_event_var.get()

    if not selected_event:
        return

    current_text = selected_event.removeprefix(
        "- "
    )

    new_text = simpledialog.askstring(
        "Edit event",
        "Event:",
        initialvalue=current_text,
        parent=root,
    )

    if not new_text:
        return

    edited_event = f"- {new_text}"

    content = journal_file.read_text(
        encoding="utf-8"
    )

    new_content = content.replace(
        selected_event,
        edited_event,
        1,
    )

    write_journal(
        journal_file,
        new_content,
    )

    refresh_events(
        journal_file,
        event_frame,
        selected_event_var,
    )


def delete_event_gui(
    root,
    journal_file,
    event_frame,
    selected_event_var,
):
    selected_event = selected_event_var.get()

    if not selected_event:
        return

    confirmed = messagebox.askyesno(
        "Delete event",
        (
            "Delete this event?"
            f"\n\n{selected_event}"
        ),
        parent=root,
    )

    if not confirmed:
        return

    content = journal_file.read_text(
        encoding="utf-8"
    )

    new_content = content.replace(
        selected_event + "\n",
        "",
        1,
    )

    if new_content == content:
        new_content = content.replace(
            selected_event,
            "",
            1,
        )

    write_journal(
        journal_file,
        new_content,
    )

    refresh_events(
        journal_file,
        event_frame,
        selected_event_var,
    )

    