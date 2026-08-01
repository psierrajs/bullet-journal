from journal_storage import (
    append_line,
    create_daily_journal,
    insert_before_section,
    replace_task,
    write_journal,
)

from terminal_ui import (
    display_journal_details,
    display_menu,
    display_tasks,
    pause,
    select_line,
    select_task,
)

from pathlib import Path
from datetime import date, timedelta

from journal_parser import (
    get_section_lines,
    get_section_positions,
    get_task_lines,
    validate_journal_content,
)

from task_actions import (
    cancel_task,
    complete_task,
    delete_task,
    edit_task,
    reopen_task,
)

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