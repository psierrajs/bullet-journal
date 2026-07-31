from pathlib import Path
from datetime import date, timedelta

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
    print("8. Exit")

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

def replace_task(content, old_task, new_task, journal_file):
    new_content = content.replace(
        old_task,
        new_task,
        1
    )

    journal_file.write_text(
        new_content,
        encoding="utf-8"
    )

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

def reopen_task(content, task_lines, journal_file):
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
        reopened_task,
        journal_file
    )

    print(f"Cancelled: {cancelled_task}")

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

def append_line(content, new_line, journal_file):
    new_content = content.rstrip() + "\n" + new_line

    journal_file.write_text(
        new_content,
        encoding="utf-8"
    )

def add_event(content, journal_file):
    event = input("Enter a new event: ").strip()

    if not event:
        print("No event entered. Nothing was added.")
        return

    event_line = f"- {event}\n"

    append_line(
        content,
        event_line,
        journal_file
    )

    print(f'Event added: "{event}"')

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

    journal_file.write_text(
        new_content,
        encoding="utf-8"
    )

def pause():
    input("Press Enter to continue...")

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

        if get_section_positions is None:
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
            print("Goodbye.")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()