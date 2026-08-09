import tkinter as tk
from tkinter import simpledialog, ttk

from datetime import date
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
        fill="both",
        expand=True,
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

    selected_task_var.set("")

    fill_task_section(
        task_frame,
        updated_tasks,
        selected_task_var,
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


def main():
    root = tk.Tk()
    root.title(f"Bullet Journal v{__version__}")
    root.geometry("900x700")

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

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

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(
        fill="x",
        pady=(0, 20),
    )

    ttk.Button(
        button_frame,
        text="Add Task",
        command=lambda: add_task_gui(
            root,
            journal_file,
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left", padx=(0, 10))

    ttk.Button(
        button_frame,
        text="Complete Task",
        command=lambda: complete_task_gui(
            journal_file,
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left")

    note_frame = create_section(
        main_frame,
        "Notes",
    )

    fill_section(
        note_frame,
        note_lines,
    )

    event_frame = create_section(
        main_frame,
        "Events",
    )

    fill_section(
        event_frame,
        event_lines,
    )

    root.mainloop()


if __name__ == "__main__":
    main()

