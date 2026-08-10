import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from datetime import date, timedelta
from pathlib import Path

from journal_parser import (
    get_section_lines,
    get_section_positions,
    get_task_lines,
)
from journal_storage import (
    create_daily_journal,
    insert_before_section,
    replace_task,
    write_journal,
)
from version import __version__


def load_today():
    today = date.today()

    journal_folder = Path("journal")
    journal_folder.mkdir(exist_ok=True)

    journal_file = journal_folder / f"{today.isoformat()}.md"

    if not journal_file.exists():
        create_daily_journal(journal_file, today)

    content = journal_file.read_text(encoding="utf-8")

    section_positions = get_section_positions(content)

    if section_positions is None:
        raise ValueError("Invalid journal structure.")

    tasks_start, notes_start, events_start = section_positions

    task_lines = get_task_lines(content)

    if task_lines is None:
        raise ValueError("Invalid journal structure.")

    note_lines = get_section_lines(
        content,
        notes_start,
        events_start,
    )

    event_lines = get_section_lines(
        content,
        events_start,
    )

    return (
        today,
        journal_file,
        task_lines,
        note_lines,
        event_lines,
    )


def fill_section(frame, lines):
    for widget in frame.winfo_children():
        widget.destroy()

    if not lines:
        ttk.Label(
            frame,
            text="No entries yet.",
        ).pack(anchor="w")
        return

    for line in lines:
        ttk.Label(
            frame,
            text=line,
        ).pack(anchor="w", pady=2)


def create_section(parent, title):
    frame = ttk.LabelFrame(
        parent,
        text=title,
        padding=10,
    )
    frame.pack(
        fill="x",
        pady=(0, 10),
    )

    return frame


def fill_task_section(
    frame,
    task_lines,
    selected_task_var,
):
    for widget in frame.winfo_children():
        widget.destroy()

    if not task_lines:
        ttk.Label(
            frame,
            text="No tasks yet.",
        ).pack(anchor="w")
        return

    for task_line in task_lines:
        ttk.Radiobutton(
            frame,
            text=task_line,
            variable=selected_task_var,
            value=task_line,
        ).pack(anchor="w", pady=2)

def get_task_summary(task_lines):
    open_count = 0
    completed_count = 0
    cancelled_count = 0
    migrated_count = 0

    for task in task_lines:
        if task.startswith("- [ ]"):
            open_count += 1
        elif task.startswith("- [x]"):
            completed_count += 1
        elif task.startswith("- [-]"):
            cancelled_count += 1
        elif task.startswith("- [>]"):
            migrated_count += 1

    total = len(task_lines)

    return (
        f"{total} tasks · "
        f"{open_count} open · "
        f"{completed_count} completed · "
        f"{cancelled_count} cancelled · "
        f"{migrated_count} migrated"
    )

def refresh_tasks(
    journal_file,
    task_frame,
    selected_task_var,
):
    updated_content = journal_file.read_text(
        encoding="utf-8"
    )

    updated_tasks = get_task_lines(updated_content)

    if updated_tasks is None:
        raise ValueError("Invalid journal structure.")

    summary_var = getattr(
        task_frame,
        "summary_var",
        None,
    )

    if summary_var is not None:
        summary_var.set(
            get_task_summary(updated_tasks)
        )

    selected_task_var.set("")

    fill_task_section(
        task_frame,
        updated_tasks,
        selected_task_var,
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
        raise ValueError("Invalid journal structure.")

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


def add_task_gui(
    root,
    journal_file,
    task_frame,
    selected_task_var,
):
    task_text = simpledialog.askstring(
        "Add task",
        "Task:",
        parent=root,
    )

    if not task_text:
        return

    content = journal_file.read_text(encoding="utf-8")
    section_positions = get_section_positions(content)

    if section_positions is None:
        raise ValueError("Invalid journal structure.")

    tasks_start, notes_start, events_start = section_positions

    insert_before_section(
        content,
        notes_start,
        f"- [ ] {task_text}",
        journal_file,
    )

    refresh_tasks(
        journal_file,
        task_frame,
        selected_task_var,
    )


def complete_task_gui(
    journal_file,
    task_frame,
    selected_task_var,
):
    selected_task = selected_task_var.get()

    if not selected_task:
        return

    if not selected_task.startswith("- [ ]"):
        return

    content = journal_file.read_text(encoding="utf-8")

    completed_task = selected_task.replace(
        "- [ ]",
        "- [x]",
        1,
    )

    replace_task(
        content,
        selected_task,
        completed_task,
        journal_file,
    )

    refresh_tasks(
        journal_file,
        task_frame,
        selected_task_var,
    )

def reopen_task_gui(
    journal_file,
    task_frame,
    selected_task_var,
):
    selected_task = selected_task_var.get()

    if not selected_task:
        return

    if selected_task.startswith("- [x]"):
        reopened_task = selected_task.replace(
            "- [x]",
            "- [ ]",
            1,
        )
    elif selected_task.startswith("- [-]"):
        reopened_task = selected_task.replace(
            "- [-]",
            "- [ ]",
            1,
        )
    else:
        return

    content = journal_file.read_text(encoding="utf-8")

    replace_task(
        content,
        selected_task,
        reopened_task,
        journal_file,
    )

    refresh_tasks(
        journal_file,
        task_frame,
        selected_task_var,
    )


def cancel_task_gui(
    journal_file,
    task_frame,
    selected_task_var,
):
    selected_task = selected_task_var.get()

    if not selected_task:
        return

    if not selected_task.startswith("- [ ]"):
        return

    content = journal_file.read_text(encoding="utf-8")

    cancelled_task = selected_task.replace(
        "- [ ]",
        "- [-]",
        1,
    )

    replace_task(
        content,
        selected_task,
        cancelled_task,
        journal_file,
    )

    refresh_tasks(
        journal_file,
        task_frame,
        selected_task_var,
    )

def edit_task_gui(
    root,
    journal_file,
    task_frame,
    selected_task_var,
):
    selected_task = selected_task_var.get()

    if not selected_task:
        return

    current_text = selected_task[6:]

    new_text = simpledialog.askstring(
        "Edit task",
        "Task:",
        initialvalue=current_text,
        parent=root,
    )

    if not new_text:
        return

    task_marker = selected_task[:5]

    edited_task = f"{task_marker} {new_text}"

    content = journal_file.read_text(
        encoding="utf-8"
    )

    replace_task(
        content,
        selected_task,
        edited_task,
        journal_file,
    )

    refresh_tasks(
        journal_file,
        task_frame,
        selected_task_var,
    )

def delete_task_gui(
    root,
    journal_file,
    task_frame,
    selected_task_var,
):
    selected_task = selected_task_var.get()

    if not selected_task:
        return

    confirmed = messagebox.askyesno(
        "Delete task",
        f"Delete this task?\n\n{selected_task}",
        parent=root,
    )

    if not confirmed:
        return

    content = journal_file.read_text(
        encoding="utf-8"
    )

    new_content = content.replace(
        selected_task + "\n",
        "",
        1,
    )

    if new_content == content:
        new_content = content.replace(
            selected_task,
            "",
            1,
        )

    write_journal(
        journal_file,
        new_content,
    )

    refresh_tasks(
        journal_file,
        task_frame,
        selected_task_var,
    )

def migrate_task_gui(
    root,
    journal_file,
    task_frame,
    selected_task_var,
):
    selected_task = selected_task_var.get()

    if not selected_task:
        return

    if not selected_task.startswith("- [ ]"):
        messagebox.showinfo(
            "Migrate task",
            "Only open tasks can be migrated.",
            parent=root,
        )
        return

    confirmed = messagebox.askyesno(
        "Migrate task",
        f"Migrate this task to tomorrow?\n\n{selected_task}",
        parent=root,
    )

    if not confirmed:
        return

    today = date.today()
    tomorrow = today + timedelta(days=1)

    journal_folder = journal_file.parent
    tomorrow_file = (
        journal_folder
        / f"{tomorrow.isoformat()}.md"
    )

    if not tomorrow_file.exists():
        create_daily_journal(
            tomorrow_file,
            tomorrow,
        )

    tomorrow_content = tomorrow_file.read_text(
        encoding="utf-8"
    )

    tomorrow_positions = get_section_positions(
        tomorrow_content
    )

    if tomorrow_positions is None:
        raise ValueError(
            "Invalid destination journal structure."
        )

    (
        tomorrow_tasks_start,
        tomorrow_notes_start,
        tomorrow_events_start,
    ) = tomorrow_positions

    task_text = selected_task[6:]

    insert_before_section(
        tomorrow_content,
        tomorrow_notes_start,
        f"- [ ] {task_text}",
        tomorrow_file,
    )

    current_content = journal_file.read_text(
        encoding="utf-8"
    )

    migrated_task = selected_task.replace(
        "- [ ]",
        "- [>]",
        1,
    )

    replace_task(
        current_content,
        selected_task,
        migrated_task,
        journal_file,
    )

    refresh_tasks(
        journal_file,
        task_frame,
        selected_task_var,
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

    content = journal_file.read_text(
        encoding="utf-8"
    )

    section_positions = get_section_positions(content)

    if section_positions is None:
        raise ValueError("Invalid journal structure.")

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
def edit_note_gui(
    root,
    journal_file,
    note_frame,
    selected_note_var,
):
    selected_note = selected_note_var.get()

    if not selected_note:
        return

    current_text = selected_note.removeprefix("- ").strip()

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
        ).pack(anchor="w", pady=2)

def refresh_events(
    journal_file,
    event_frame,
    selected_event_var,
):
    updated_content = journal_file.read_text(
        encoding="utf-8"
    )

    updated_positions = get_section_positions(
        updated_content
    )

    if updated_positions is None:
        raise ValueError("Invalid journal structure.")

    (
        updated_tasks_start,
        updated_notes_start,
        updated_events_start,
    ) = updated_positions

    updated_events = get_section_lines(
        updated_content,
        updated_events_start,
    )

    selected_event_var.set("")

    fill_event_section(
        event_frame,
        updated_events,
        selected_event_var,
    )

def fill_note_section(
    frame,
    note_lines,
    selected_note_var,
):
    for widget in frame.winfo_children():
        widget.destroy()

    if not note_lines:
        ttk.Label(
            frame,
            text="No notes yet.",
        ).pack(anchor="w")
        return

    for note_line in note_lines:
        ttk.Radiobutton(
            frame,
            text=note_line,
            variable=selected_note_var,
            value=note_line,
        ).pack(anchor="w", pady=2)

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
        f"Delete this note?\n\n{selected_note}",
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

def edit_event_gui(
    root,
    journal_file,
    event_frame,
    selected_event_var,
):
    selected_event = selected_event_var.get()

    if not selected_event:
        return

    current_text = selected_event.removeprefix("- ").strip()

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
        f"Delete this event?\n\n{selected_event}",
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

def main():
    root = tk.Tk()
    root.title(f"Bullet Journal v{__version__}")
    root.geometry("900x850")

    container = ttk.Frame(root)
    container.pack(
        fill="both",
        expand=True,
    )

    canvas = tk.Canvas(
        container,
        highlightthickness=0,
    )

    scrollbar = ttk.Scrollbar(
        container,
        orient="vertical",
        command=canvas.yview,
    )

    canvas.configure(
        yscrollcommand=scrollbar.set,
    )

    scrollbar.pack(
        side="right",
        fill="y",
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True,
    )

    main_frame = ttk.Frame(
        canvas,
        padding=20,
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=main_frame,
        anchor="nw",
    )

    def update_scroll_region(event):
        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    def resize_content(event):
        canvas.itemconfigure(
            canvas_window,
            width=event.width,
        )

    main_frame.bind(
        "<Configure>",
        update_scroll_region,
    )

    canvas.bind(
        "<Configure>",
        resize_content,
    )

    def on_mousewheel(event):
        if event.delta > 0:
            canvas.yview_scroll(-1, "units")
        elif event.delta < 0:
            canvas.yview_scroll(1, "units")

    canvas.bind_all(
        "<MouseWheel>",
        on_mousewheel,
    )

    (
        today,
        journal_file,
        task_lines,
        note_lines,
        event_lines,
    ) = load_today()

    ttk.Label(
        main_frame,
        text="Bullet Journal",
        font=("Helvetica", 24, "bold"),
    ).pack(anchor="w")

    ttk.Label(
        main_frame,
        text=today.strftime("%A, %d %B %Y"),
    ).pack(anchor="w", pady=(0, 20))

    selected_task_var = tk.StringVar()

    task_frame = create_section(
        main_frame,
        "Tasks",
    )

    fill_task_section(
        task_frame,
        task_lines,
        selected_task_var,
    )

    task_summary_var = tk.StringVar(
        value=get_task_summary(task_lines)
    )

    task_frame.summary_var = task_summary_var

    summary_frame = ttk.Frame(
        main_frame,
        padding=(10, 8),
    )

    summary_frame.pack(
        fill="x",
        pady=(0, 10),
    )

    ttk.Label(
        summary_frame,
        text="Task Summary",
        font=("Helvetica", 14, "bold"),
    ).pack(anchor="w")

    ttk.Label(
        summary_frame,
        textvariable=task_summary_var,
        font=("Helvetica", 12),
    ).pack(
        anchor="w",
        pady=(4, 0),
    )

    ttk.Separator(
        summary_frame,
        orient="horizontal",
    ).pack(
        fill="x",
        pady=(8, 0),
    )
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(
        fill="x",
        pady=(0, 20),
    )

    primary_buttons = ttk.Frame(button_frame)
    primary_buttons.pack(
        anchor="w",
        pady=(0, 8),
    )

    status_buttons = ttk.Frame(button_frame)
    status_buttons.pack(anchor="w")

    ttk.Button(
        primary_buttons,
        text="Add Task",
        command=lambda: add_task_gui(
            root,
            journal_file,
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        primary_buttons,
        text="Edit Task",
        command=lambda: edit_task_gui(
            root,
            journal_file,
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        primary_buttons,
        text="Delete Task",
        command=lambda: delete_task_gui(
            root,
            journal_file,
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left")

    ttk.Button(
        status_buttons,
        text="Complete",
        command=lambda: complete_task_gui(
            journal_file,
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        status_buttons,
        text="Reopen",
        command=lambda: reopen_task_gui(
            journal_file,
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        status_buttons,
        text="Cancel",
        command=lambda: cancel_task_gui(
            journal_file,
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        status_buttons,
        text="Migrate",
        command=lambda: migrate_task_gui(
            root,
            journal_file,
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left")

    selected_note_var = tk.StringVar()

    note_frame = create_section(
        main_frame,
        "Notes",
    )

    fill_note_section(
        note_frame,
        note_lines,
        selected_note_var,
    )

    note_button_frame = ttk.Frame(main_frame)
    note_button_frame.pack(
        anchor="w",
        pady=(0, 20),
    )

    ttk.Button(
        note_button_frame,
        text="Add Note",
        command=lambda: add_note_gui(
            root,
            journal_file,
            note_frame,
            selected_note_var,
        ),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        note_button_frame,
        text="Edit Note",
        command=lambda: edit_note_gui(
            root,
            journal_file,
            note_frame,
            selected_note_var,
        ),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        note_button_frame,
        text="Delete Note",
        command=lambda: delete_note_gui(
            root,
            journal_file,
            note_frame,
            selected_note_var,
        ),
    ).pack(side="left")

    selected_event_var = tk.StringVar()

    event_frame = create_section(
        main_frame,
        "Events",
    )

    fill_event_section(
        event_frame,
        event_lines,
        selected_event_var,
    )

    event_button_frame = ttk.Frame(main_frame)
    event_button_frame.pack(
        anchor="w",
        pady=(0, 20),
    )

    ttk.Button(
        event_button_frame,
        text="Add Event",
        command=lambda: add_event_gui(
            root,
            journal_file,
            event_frame,
            selected_event_var,
        ),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        event_button_frame,
        text="Edit Event",
        command=lambda: edit_event_gui(
            root,
            journal_file,
            event_frame,
            selected_event_var,
        ),
    ).pack(side="left", padx=(0, 8))

    ttk.Button(
        event_button_frame,
        text="Delete Event",
        command=lambda: delete_event_gui(
            root,
            journal_file,
            event_frame,
            selected_event_var,
        ),
    ).pack(side="left")

    root.mainloop()


if __name__ == "__main__":
    main()



