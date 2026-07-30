from pathlib import Path
from datetime import date

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

def display_menu():
    print("\nChoose an option:")
    print("1. Add a task")
    print("2. Complete a task")
    print("3. Reopen a task")
    print("4. Add a note")
    print("5. Add an event")
    print("6. Cancel a task")
    print("7. Exit")

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
    task = input("Enter a new task: ").strip()

    if not task:
        print("No task entered, Nothing was added.")
        return

    task_line = f"- [ ] {task}\n"

    insert_before_section(
    content,
    notes_start,
    task_line,
    journal_file
)

    print(f'Task added: "{task}"')

def replace_task(content, old_task, new_task, journal_file):
    new_content = content.replace(
        old.task,
        new.task,
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
        input("Press Enter to continue...")
        return

    if selected_task.startswith("- [-]"):
        print("A cancelled task must be reopened first.")
        input("Press Enter to continue...")
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
        input("Press Enter to continue...")
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
        input("Press Enter to continue...")
        return

    if selected_task.lower().startswith("- [x]"):
        print("A completed task cannot be cancelled.")
        input("Press Enter to continue...")
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

def add_note(content, events_start, journal_file):
    note = input("Enter a new note: ").strip()

    if not note:
        print("No note entered. Nothing was added.")
        return

    note_line = f"- {note}\n"

    insert_before_section(
    content,
    events_start,
    note_line,
    journal_file
)

    print(f'Note added: "{note}"')

def add_event(content, journal_file):
    event = input("Enter a new event: ").strip()

    if not event:
        print("No event entered. Nothing was added.")
        return

    event_line = f"- {event}\n"

    current_content = journal_file.read_text(encoding="utf-8")
    new_content = current_content.rstrip() + "\n" + event_line

    journal_file.write_text(
        new_content,
        encoding="utf-8"
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

        task_lines = get_task_lines(content)

        if task_lines is None:
            print("Error: Invalid journal structure.")
            break

        display_tasks(task_lines)

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
            print("Goodbye.")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()