from pathlib import Path
from datetime import date, timedelta
import shutil

def get_task_lines(content):
    tasks_header = "## Tasks\n"
    notes_header = "## Notes"

    tasks_start = content.find(tasks_header)

    if tasks_start == -1:
        return None

    notes_start = content.find(notes_header, tasks_start)

    if notes_start == -1:
        return None

    tasks_section = content[
        tasks_start + len(tasks_header):notes_start
    ]

    task_lines = []

    for line in tasks_section.splitlines():
        if line.startswith("- ["):
            task_lines.append(line)

    return task_lines

def get_section_lines(content, section_start, next_section_start=None):
    if next_section_start is None:
        section = content[section_start:]
    else:
        section = content[section_start:next_section_start]

    lines = []

    for line in section.splitlines()[1:]:
        stripped_line = line.strip()

        if stripped_line:
            lines.append(stripped_line)

    return lines

def get_section_positions(content):
    tasks_start = content.find("## Tasks\n")
    notes_start = content.find("## Notes")
    events_start = content.find("## Events")

    if tasks_start == -1:
        return None

    if notes_start == -1:
        return None

    if events_start == -1:
        return None

    return tasks_start, notes_start, events_start

def display_tasks(task_lines):
    print("\nToday's tasks:\n")

    if not task_lines:
        print("No tasks yet.")
        return

    for number, task_line in enumerate(task_lines, start=1):
        print(f"{number}. {task_line}")

def display_journal_details(note_lines, event_lines):
    print("\nToday's notes:\n")

    if not note_lines:
        print("No notes yet.")
    else:
        for note_line in note_lines:
            print(note_line)

    print("\nToday's events:\n")

    if not event_lines:
        print("No events yet.")
    else:
        for event_line in event_lines:
            print(event_line)

def display_menu():
    print("\nChoose an option:")
    print("1. Add a task")
    print("2. Complete a task")
    print("3. Reopen a task")
    print("4. Add a note")
    print("5. Add an event")
    print("6. Cancel a task")
    print("7. Migrate a task.")
    print("8. View another day")
    print("9. List journal days")
    print("10. Search journals")
    print("11. List pending tasks")
    print("12. Review yesterday")
    print("13. Edit a task")
    print("14. Delete a task")
    print("15. Edit a note")
    print("16. Delete a note")
    print("17. Edit an event")
    print("18. Delete an event")
    print("19. Restore today's backup")
    print("20. Exit")

def select_task(task_lines, prompt):
    if not task_lines:
        return None

    task_number_text = input(prompt).strip()

    if not task_number_text.isdigit():
        print("Please enter a valid number.")
        return None

    task_number = int(task_number_text)

    if task_number < 1 or task_number > len(task_lines):
        print("That task number does not exist.")
        return None

    return task_lines[task_number -1]

def select_line(lines, prompt):
    if not lines:
        return None

    line_number_text = input(prompt).strip()

    if not line_number_text.isdigit():
        print("Please enter a valid number.")
        return None

    line_number = int(line_number_text)

    if line_number < 1 or line_number > len(lines):
        print("That number does not exist.")
        return None

    return lines[line_number - 1]

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

def write_journal(journal_file, content):
    temporary_file = journal_file.with_suffix(
        journal_file.suffix + ".tmp"
    )

    backup_file = journal_file.with_suffix(
        journal_file.suffix + ".bak"
    )

    temporary_file.write_text(
        content,
        encoding="utf-8"
    )

    if journal_file.exists():
        shutil.copy2(
            journal_file,
            backup_file
        )

    temporary_file.replace(journal_file)

def restore_backup(journal_file):
    backup_file = journal_file.with_suffix(
        journal_file.suffix + ".bak"
    )

    if not backup_file.exists():
        print("No backup file exists for today.")
        pause()
        return

    print(f"Backup found: {backup_file.name}")

    confirmation = input(
        "Restore this backup? Current changes will be replaced. [y/N]: "
    ).strip().lower()

    if confirmation != "y":
        print("Restore cancelled.")
        pause()
        return

    backup_content = backup_file.read_text(
        encoding="utf-8"
    )

    write_journal(
        journal_file,
        backup_content
    )

    print("Backup restored successfully.")
    pause()

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

def add_note(content, events_start, journal_file):
    while True:
        note = input(
            "Enter a new note, or press Enter to finish: "
        ).strip()

        if not note:
            return

        note_line = f"- {note}\n"

        insert_before_section(
            content,
            events_start,
            note_line,
            journal_file
        )

        print(f'Note added: "{note}"')

        content = journal_file.read_text(encoding="utf-8")

        section_positions = get_section_positions(content)

        if section_positions is None:
            print("Error: Invalid journal structure.")
            return

        _, _, events_start = section_positions

def edit_note(
    content,
    note_lines,
    journal_file
):
    if not note_lines:
        print("There are no notes to edit.")
        pause()
        return

    print("\nToday's notes:\n")

    for number, note_line in enumerate(
        note_lines,
        start=1
    ):
        print(f"{number}. {note_line}")

    selected_note = select_line(
        note_lines,
        "Enter the number of the note to edit: "
    )

    if selected_note is None:
        pause()
        return

    new_text = input(
        "Enter the new note text: "
    ).strip()

    if not new_text:
        print("No note text entered. Nothing was changed.")
        pause()
        return

    edited_note = f"- {new_text}"

    new_content = content.replace(
        selected_note,
        edited_note,
        1
    )

    write_journal(
        journal_file,
        new_content
    )

    print(f'Note updated: "{new_text}"')
    pause()

def delete_note(content, note_lines, journal_file):
    if not note_lines:
        print("There are no notes to delete.")
        pause()
        return

    print("\nToday's notes:\n")

    for number, note_line in enumerate(
        note_lines,
        start=1
    ):
        print(f"{number}. {note_line}")

    selected_note = select_line(
        note_lines,
        "Enter the number of the note to delete: "
    )

    if selected_note is None:
        pause()
        return

    print(f"\nSelected note: {selected_note}")

    confirmation = input(
        "Delete this note? [y/N]: "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        pause()
        return

    new_content = content.replace(
        selected_note + "\n",
        "",
        1
    )

    if new_content == content:
        new_content = content.replace(
            selected_note,
            "",
            1
        )

    write_journal(
        journal_file,
        new_content
    )

    print("Note deleted.")
    pause()

def append_line(content, new_line, journal_file):
    new_content = content.rstrip() + "\n" + new_line

    write_journal(
        journal_file,
        new_content
    )

def add_event(content, journal_file):
    while True:
        event = input(
            "Enter a new event, or press Enter to finish: "
        ).strip()

        if not event:
            return

        event_line = f"- {event}\n"

        append_line(
            content,
            event_line,
            journal_file
        )

        print(f'Event added: "{event}"')

        content = journal_file.read_text(
            encoding="utf-8"
        )

def edit_event(
    content,
    event_lines,
    journal_file
):
    if not event_lines:
        print("There are no events to edit.")
        pause()
        return

    print("\nToday's events:\n")

    for number, event_line in enumerate(
        event_lines,
        start=1
    ):
        print(f"{number}. {event_line}")

    selected_event = select_line(
        event_lines,
        "Enter the number of the event to edit: "
    )

    if selected_event is None:
        pause()
        return

    new_text = input(
        "Enter the new event text: "
    ).strip()

    if not new_text:
        print("No event text entered. Nothing was changed.")
        pause()
        return

    edited_event = f"- {new_text}"

    new_content = content.replace(
        selected_event,
        edited_event,
        1
    )

    write_journal(
        journal_file,
        new_content
    )

    print(f'Event updated: "{new_text}"')
    pause()


def delete_event(content, event_lines, journal_file):
    if not event_lines:
        print("There are no events to delete.")
        pause()
        return

    print("\nToday's events:\n")

    for number, event_line in enumerate(
        event_lines,
        start=1
    ):
        print(f"{number}. {event_line}")

    selected_event = select_line(
        event_lines,
        "Enter the number of the event to delete: "
    )

    if selected_event is None:
        pause()
        return

    print(f"\nSelected event: {selected_event}")

    confirmation = input(
        "Delete this event? [y/N]: "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        pause()
        return

    new_content = content.replace(
        selected_event + "\n",
        "",
        1
    )

    if new_content == content:
        new_content = content.replace(
            selected_event,
            "",
            1
        )

    write_journal(
        journal_file,
        new_content
    )

    print("Event deleted.")
    pause()

def create_daily_journal(journal_file, today):
    if journal_file.exists():
        return

    journal_file.write_text(
        f"# {today.strftime('%A, %d %B %Y')}\n\n"
        "## Tasks\n\n"
        "## Notes\n\n"
        "## Events\n",
        encoding="utf-8"        
    )

def insert_before_section(
    content,
    section_start,
    new_line,
    journal_file
):
    before_section = content[:section_start].rstrip()
    after_section = content[section_start:]

    new_content = (
        before_section
        + "\n"
        + new_line
        + "\n"
        + after_section
    )

    write_journal(
        journal_file,
        new_content
    )

def pause():
    input("Press Enter to continue...")

def view_journal(journal_folder):
    date_text = input(
        "Enter the date to view (YYYY-MM-DD): "
    ).strip()

    try:
        selected_date = date.fromisoformat(date_text)
    except ValueError:
        print("Please enter a valid date in YYYY-MM-DD format.")
        pause()
        return

    filename = f"{selected_date.isoformat()}.md"
    selected_file = journal_folder / filename

    if not selected_file.exists():
        print(f"No journal exists for {date_text}.")
        pause()
        return

    content = selected_file.read_text(encoding="utf-8")

    print("\n" + "=" * 40)
    print(content)
    print("=" * 40)

    pause()

def list_journals(journal_folder):
    journal_files = sorted(journal_folder.glob("*.md"))

    if not journal_files:
        print("No journal files found.")
        pause()
        return

    print("\nAvailable journal days:\n")

    for journal_file in journal_files:
        try:
            journal_date = date.fromisoformat(journal_file.stem)
        except ValueError:
            continue

        formatted_date = journal_date.strftime(
            "%A, %d %B %Y"
        )

        print(
            f"{journal_date.isoformat()} — "
            f"{formatted_date}"
        )

    pause()

def search_journals(journal_folder):
    search_text = input(
        "Enter text to search for: "
    ).strip()

    if not search_text:
        print("No search text entered.")
        pause()
        return

    journal_files = sorted(journal_folder.glob("*.md"))
    matches_found = False

    print(f'\nSearch results for "{search_text}":\n')

    for journal_file in journal_files:
        content = journal_file.read_text(
            encoding="utf-8"
        )

        for line_number, line in enumerate(
            content.splitlines(),
            start=1
        ):
            if search_text.lower() in line.lower():
                matches_found = True

                print(
                    f"{journal_file.stem}, "
                    f"line {line_number}: {line}"
                )

    if not matches_found:
        print("No matches found.")

    pause()

def list_pending_tasks(journal_folder):
    journal_files = sorted(journal_folder.glob("*.md"))
    pending_tasks = []

    for journal_file in journal_files:
        content = journal_file.read_text(encoding="utf-8")
        task_lines = get_task_lines(content)

        if task_lines is None:
            continue

        for task_line in task_lines:
            if task_line.startswith("- [ ]"):
                pending_tasks.append(
                    (journal_file.stem, task_line)
                )

    print("\nPending tasks:\n")

    if not pending_tasks:
        print("No pending tasks found.")
        pause()
        return

    for number, (journal_date, task_line) in enumerate(
        pending_tasks,
        start=1
    ):
        print(f"{number}. {journal_date}: {task_line}")

    pause()

def review_previous_day(
    journal_folder,
    journal_file,
    today
):
    previous_date = today - timedelta(days=1)
    previous_file = (
        journal_folder
        / f"{previous_date.isoformat()}.md"
    )

    if not previous_file.exists():
        print(
            f"No journal exists for "
            f"{previous_date.isoformat()}."
        )
        pause()
        return

    previous_content = previous_file.read_text(
        encoding="utf-8"
    )

    previous_tasks = get_task_lines(
        previous_content
    )

    if previous_tasks is None:
        print("Error: Invalid previous journal structure.")
        pause()
        return

    pending_tasks = [
        task_line
        for task_line in previous_tasks
        if task_line.startswith("- [ ]")
    ]

    print(
        f"\nPending tasks from "
        f"{previous_date.isoformat()}:\n"
    )

    if not pending_tasks:
        print("No pending tasks from yesterday.")
        pause()
        return

    for number, task_line in enumerate(
        pending_tasks,
        start=1
    ):
        print(f"{number}. {task_line}")

    print("\n1. Migrate a task to today")
    print("2. Return to the main menu")

    choice = input("\nOption: ").strip()

    if choice == "2":
        return

    if choice != "1":
        print("Invalid option.")
        pause()
        return

    selected_task = select_task(
        pending_tasks,
        "Enter the task number to migrate: "
    )

    if selected_task is None:
        pause()
        return

    migrated_task = selected_task.replace(
        "- [ ]",
        "- [>]",
        1
    )

    replace_task(
        previous_content,
        selected_task,
        migrated_task,
        previous_file
    )

    today_content = journal_file.read_text(
        encoding="utf-8"
    )

    section_positions = get_section_positions(
        today_content
    )

    if section_positions is None:
        print("Error: Invalid journal structure.")
        pause()
        return

    _, notes_start, _ = section_positions

    insert_before_section(
        today_content,
        notes_start,
        selected_task + "\n",
        journal_file
    )

    print(
        f"Migrated from {previous_date.isoformat()}: "
        f"{selected_task}"
    )

    pause()

def main():
    today = date.today()
    filename = f"{today.isoformat()}.md"

    journal_folder = Path("journal")
    journal_folder.mkdir(exist_ok=True)

    journal_file = journal_folder / filename


    if not journal_file.exists():
        create_daily_journal(journal_file, today)


    while True:
        content = journal_file.read_text(encoding="utf-8")

        section_positions = get_section_positions(content)

        if section_positions is None:
            print("Error, Invalid journal structure.")
            break

        tasks_start, notes_start, events_start = section_positions

        note_lines = get_section_lines(
            content,
            notes_start,
            events_start
        )

        event_lines = get_section_lines(
            content,
            events_start
        )

        task_lines = get_task_lines(content)

        if task_lines is None:
            print("Error: Invalid journal structure.")
            break

        display_tasks(task_lines)
        display_journal_details(note_lines, event_lines)
        display_menu()

        choice = input("\nOption: ").strip()

        if choice == "1":
            add_task(content, notes_start, journal_file)

        elif choice == "2":
            complete_task(content, task_lines, journal_file)

        elif choice == "3":
            reopen_task(content, task_lines, journal_file)

        elif choice == "4":
            add_note(content, events_start, journal_file)

        elif choice == "5":
            add_event(content, journal_file)

        elif choice == "6":
            cancel_task(content, task_lines, journal_file)

        elif choice == "7":
            migrate_task(
                content,
                task_lines,
                journal_file,
                journal_folder,
                today
        )

        elif choice == "8":
            view_journal(journal_folder)

        elif choice == "9":
            list_journals(journal_folder)

        elif choice == "10":
            search_journals(journal_folder)

        elif choice == "11":
            list_pending_tasks(journal_folder)

        elif choice == "12":
            review_previous_day(
                journal_folder,
                journal_file,
                today
        )

        elif choice == "13":
            edit_task(
                content,
                task_lines,
                journal_file
        )

        elif choice == "14":
            delete_task(
                content,
                task_lines,
                journal_file
        )

        elif choice == "15":
            edit_note(
                content,
                note_lines,
                journal_file
            )

        elif choice == "16":
            delete_note(
                content,
                note_lines,
                journal_file
            )

        elif choice == "17":
            edit_event(
                content,
                event_lines,
                journal_file
            )

        elif choice == "18":
            delete_event(
                content,
                event_lines,
                journal_file
            )

        elif choice == "19":
            restore_backup(journal_file)

        elif choice == "20":
            print("Goodbye.")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()