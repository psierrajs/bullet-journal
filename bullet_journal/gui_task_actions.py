import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import date, timedelta

from .gui_helpers import refresh_journal_status
from .journal_parser import (
    get_section_positions,
    get_task_lines,
)
from .journal_storage import (
    create_daily_journal,
    insert_before_section,
    replace_task,
    write_journal,
)


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
        ).pack(
            anchor="w",
            pady=2,
        )


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

    updated_tasks = get_task_lines(
        updated_content
    )

    if updated_tasks is None:
        raise ValueError(
            "Invalid journal structure."
        )

    summary_var = getattr(
        task_frame,
        "summary_var",
        None,
    )

    if summary_var is not None:
        summary_var.set(
            get_task_summary(
                updated_tasks
            )
        )

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

    section_positions = get_section_positions(
        content
    )

    if section_positions is None:
        raise ValueError(
            "Invalid journal structure."
        )

    (
        tasks_start,
        notes_start,
        events_start,
    ) = section_positions

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

    refresh_journal_status(
        journal_file,
        task_frame,
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

    content = journal_file.read_text(
        encoding="utf-8"
    )

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

    content = journal_file.read_text(
        encoding="utf-8"
    )

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

    content = journal_file.read_text(
        encoding="utf-8"
    )

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

    edited_task = (
        f"{task_marker} {new_text}"
    )

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
        (
            "Delete this task?"
            f"\n\n{selected_task}"
        ),
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

    source_date = date.fromisoformat(
        journal_file.stem
    )

    destination_date = (
        source_date
        + timedelta(days=1)
    )

    confirmed = messagebox.askyesno(
        "Migrate task",
        (
            "Migrate this task to "
            f"{destination_date.isoformat()}?"
            f"\n\n{selected_task}"
        ),
        parent=root,
    )

    if not confirmed:
        return

    journal_folder = journal_file.parent

    destination_file = (
        journal_folder
        / f"{destination_date.isoformat()}.md"
    )

    if not destination_file.exists():
        create_daily_journal(
            destination_file,
            destination_date,
        )

    destination_content = (
        destination_file.read_text(
            encoding="utf-8"
        )
    )

    destination_positions = (
        get_section_positions(
            destination_content
        )
    )

    if destination_positions is None:
        raise ValueError(
            "Invalid destination "
            "journal structure."
        )

    (
        destination_tasks_start,
        destination_notes_start,
        destination_events_start,
    ) = destination_positions

    task_text = selected_task[6:]

    insert_before_section(
        destination_content,
        destination_notes_start,
        f"- [ ] {task_text}",
        destination_file,
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
    