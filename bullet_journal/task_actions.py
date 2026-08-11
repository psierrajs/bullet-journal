from datetime import timedelta

from .journal_parser import get_section_positions
from .journal_storage import (
    create_daily_journal,
    insert_before_section,
    replace_task,
    write_journal,
)
from .terminal_ui import pause, select_task

def complete_task(content, task_lines, journal_file):
    if not task_lines:
        print("There are no tasks to complete.")
        return

    selected_task = select_task(
        task_lines,
        "Enter the number of the completed task: "
    )

    if selected_task is None:
        return

    if selected_task.lower().startswith("- [x]"):
        print("That task is already completed.")
        pause()
        return

    if selected_task.startswith("- [-]"):
        print("A cancelled task must be reopened first.")
        pause()
        return

    completed_task = selected_task.replace(
        "- [ ]",
        "- [x]",
        1)

    replace_task(
        content,
        selected_task,
        completed_task,
        journal_file
    )

    print(f"Completed: {completed_task}")

def cancel_task(content, task_lines, journal_file):
    if not task_lines:
        print("There are no tasks to cancel.")
        return

    selected_task = select_task(
        task_lines,
        "Enter the number of the task to cancel: "
    )

    if selected_task is None:
        return

    if selected_task.startswith("- [-]"):
        print("That task is already cancelled.")
        pause()
        return

    if selected_task.lower().startswith("- [x]"):
        print("A completed task cannot be cancelled.")
        pause()
        return

    cancelled_task = selected_task.replace(
        "- [ ]",
        "- [-]",
        1
    )

    replace_task(
        content,
        selected_task,
        cancelled_task,
        journal_file
    )

    print(f"Cancelled: {cancelled_task}")

def edit_task(content, task_lines, journal_file):
    if not task_lines:
        print("There are no tasks to edit.")
        pause()
        return

    selected_task = select_task(
        task_lines,
        "Enter the number of the task to edit: "
    )

    if selected_task is None:
        pause()
        return

    new_text = input(
        "Enter the new task text: "
    ).strip()

    if not new_text:
        print("No task text entered. Nothing was changed.")
        pause()
        return

    if selected_task.startswith("- [ ]"):
        task_marker = "- [ ]"

    elif selected_task.lower().startswith("- [x]"):
        task_marker = "- [x]"

    elif selected_task.startswith("- [-]"):
        task_marker = "- [-]"

    elif selected_task.startswith("- [>]"):
        task_marker = "- [>]"

    else:
        print("Error: Unknown task status.")
        pause()
        return

    edited_task = f"{task_marker} {new_text}"

    replace_task(
        content,
        selected_task,
        edited_task,
        journal_file
    )

    print(f"Task updated: {edited_task}")
    pause()

def delete_task(content, task_lines, journal_file):
    if not task_lines:
        print("There are no tasks to delete.")
        pause()
        return

    selected_task = select_task(
        task_lines,
        "Enter the number of the task to delete: "
    )

    if selected_task is None:
        pause()
        return

    print(f"\nSelected task: {selected_task}")

    confirmation = input(
        "Delete this task? [y/N]: "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        pause()
        return

    new_content = content.replace(
        selected_task + "\n",
        "",
        1
    )

    if new_content == content:
        new_content = content.replace(
            selected_task,
            "",
            1
        )

    write_journal(
        journal_file,
        new_content
    )

    print("Task deleted.")
    pause()

def reopen_task(
    content,
    task_lines,
    journal_file
):
    if not task_lines:
        print("There are no tasks to reopen.")
        return

    selected_task = select_task(
        task_lines,
        "Enter the number of the task to reopen: "
    )

    if selected_task is None:
        return

    if selected_task.lower().startswith("- [x]"):
        reopened_task = selected_task.replace(
            "- [x]",
            "- [ ]",
            1
        )

    elif selected_task.startswith("- [-]"):
        reopened_task = selected_task.replace(
            "- [-]",
            "- [ ]",
            1
        )

    else:
        print("That task is already open.")
        pause()
        return

    replace_task(
        content,
        selected_task,
        reopened_task,
        journal_file
    )

    print(f"Reopened: {reopened_task}")


def add_task(content, notes_start, journal_file):
    while True:
        task = input(
            "Enter a new task, or press Enter to finish: "
        ).strip()

        if not task:
            return

        task_line = f"- [ ] {task}\n"

        insert_before_section(
            content,
            notes_start,
            task_line,
            journal_file
        )

        print(f'Task added: "{task}"')

        content = journal_file.read_text(encoding="utf-8")
        section_positions = get_section_positions(content)

        if section_positions is None:
            print("Error: Invalid journal structure.")
            return

        _, notes_start, _ = section_positions



def migrate_task(
    content,
    task_lines,
    journal_file,
    journal_folder,
    today
):

    if not task_lines:
        print("There are no tasks to migrate.")
        return

    selected_task = select_task(
        task_lines,
        "Enter the number of the task to migrate: "
    )

    if selected_task is None:
        return

    if selected_task.lower().startswith("- [x]"):
        print("A completed task cannot be migrated.")
        pause()
        return

    if selected_task.startswith("- [-]"):
        print("A cancelled task cannot be migrated.")
        pause()
        return

    if selected_task.startswith("- [>]"):
        print("That task has already been migrated.")
        pause()
        return

    tomorrow = today + timedelta(days=1)

    tomorrow_filename = f"{tomorrow.isoformat()}.md"
    tomorrow_file = journal_folder / tomorrow_filename

    create_daily_journal(tomorrow_file, tomorrow)

    migrated_task = selected_task.replace(
        "- [ ]",
        "- [>]",
        1
    )

    replace_task(
        content,
        selected_task,
        migrated_task,
        journal_file
    )

    tomorrow_content = tomorrow_file.read_text(
        encoding="utf-8"
    )

    tomorrow_positions = get_section_positions(
        tomorrow_content
    )

    if tomorrow_positions is None:
        print("Error: Invalid structure in tomorrow's journal.")
        return

    _, tomorrow_notes_start, _ = tomorrow_positions

    new_task = selected_task

    insert_before_section(
        tomorrow_content,
        tomorrow_notes_start,
        new_task + "\n",
        tomorrow_file
    )

    print(f"Migrated to {tomorrow.isoformat()}: {migrated_task}")
    pause()