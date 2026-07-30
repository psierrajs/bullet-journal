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

def display_tasks(task_lines):
    print("\nToday's tasks:\n")

    if not task_lines:
        print("No tasks yet.")
        return

    for number, task_line in enumerate(task_lines, start=1):
        print(f"{number}. {task_line}")

def add_task(content, notes_start, journal_file):
    task = input("Enter a new task: ").strip()

    if not task:
        print("No task entered, Nothing was added.")
        return

    task_line = f"- [ ] {task}\n"

    before_notes = content[:notes_start].rstrip()
    after_notes = content[notes_start:]

    new_content = (
        before_notes
        + "\n"
        + task_line
        + "\n"
        + after_notes
    )

    journal_file.write_text(
        new_content,
        encoding="utf-8"
    )

    print(f'Task added: "{task}"')

def completed_task(content, task_lines, journal_file):
    if not task_lines:
        print("There are no tasks to complete.")
        return

    task_number_text = input(
        "Enter the number of the completed task: "
        ).strip()

    if not task_number_text.isdigit():
        print("Please enter a valid number.")
        return

    task_number = int(task_number_text)

    if task_number < 1 or task_number > len(task_lines):
        print("That task number does not exist.")
        return

    selected_task = task_lines[task_number - 1]

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

    new_content = content.replace(
        selected_task,
        completed_task,
        1
    )

    journal_file.write_text(
        new_content,
        encoding="utf-8"
    )

    print(f"Completed: {completed_task}")

def reopen_task(content, task_lines, journal_file):
    if not task_lines:
        print("There are no tasks to reopen")
        return

    task_number_text = input(
        "Enter the number of the task to reopen: "
    ).strip()

    if not task_number_text.isdigit():
        print("Please enter a valid number.")
        return

    task_number = int(task_number_text)

    if task_number < 1 or task_number > len(task_lines):
        print("That task number does not exist.")
        return

    selected_task = task_lines[task_number - 1]

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
        input("Press Enter to continue")
        return

    new_content = content.replace(
        selected_task,
        reopened_task,1
    )

    journal_file.write_text(
        new_content,
        encoding="utf-8"
    )

    print(f"Reopened: {reopened_task}")

def cancel_task(content, task_lines, journal_file):
    if not task_lines:
        print("There are no tasks to cancel.")
        return

    task_number_text = input(
        "Enter the number of the task to cancel: "
        ).strip()

    if not task_number_text.isdigit():
        print("Please enter a valid number.")
        return

    task_number = int(task_number_text)

    if task_number < 1 or task_number > len(task_lines):
        print("That task number does not exist.")
        return

    selected_task = task_lines[task_number - 1]

    if selected_task.startswith("- [-]"):
        print("\nThe task is already cancelled.")
        input("Press enter to continue...")
        return

    if selected_task.lower().startswith("- [x]"):
        print("\nA completed task cannot be cancelled.")
        input("Press enter to continue...")
        return

    cancelled_task = selected_task.replace(
        "- [ ]",
        "- [-]",
        1
    )

    new_content = content.replace(
        selected_task,
        cancelled_task,
        1
    )

    journal_file.write_text(
        new_content,
        encoding="utf-8"
    )

    print(f"\nCancelled: {cancelled_task}")
    input("Press Enter to continue...")

def add_note(content, notes_start, journal_file):
    note = input("Enter a new note: ").strip()

    if not note:
        print("No note entered. Nothing was added.")
        return

    events_header = "## Events"
    events_start = content.find(events_header, notes_start)

    if events_start == -1:
        print("Error: Events section not found.")
        return

    note_line = f"- {note}\n"

    before_events = content[:events_start].rstrip()
    after_events = content[events_start:]

    new_content = (
        before_events
        + "\n"
        + note_line
        + "\n"
        + after_events
    )

    journal_file.write_text(
        new_content,
        encoding="utf-8"
    )

    print(f'Note added: "{note}"')


today = date.today()
filename = f"{today.isoformat()}.md"

journal_folder = Path("journal")
journal_folder.mkdir(exist_ok=True)

journal_file = journal_folder / filename


if not journal_file.exists():
    journal_file.write_text(
        f"# {today.strftime('%A, %d %B %Y')}\n\n"
        "## Tasks\n\n"
        "## Notes\n\n"
        "## Events\n",
        encoding="utf-8"
    )


while True:
    content = journal_file.read_text(encoding="utf-8")

    tasks_header = "## Tasks\n"
    notes_header = "## Notes"

    tasks_start = content.find(tasks_header)
    notes_start = content.find(notes_header, tasks_start)

    if tasks_start == -1:
        print("Error: Tasks section not found.")
        break

    if notes_start == -1:
        print("Error: Notes section not found.")
        break

    task_lines = get_task_lines(content)

    if task_lines is None:
        print("Error: Invalid journal structure.")
        break

    print("\nToday's tasks:\n")

    display_tasks(task_lines)

    print("\nChoose an option:")
    print("1. Add a task")
    print("2. Complete a task")
    print("3. Reopen a task")
    print("4. Add a note")
    print("5. Add an event")
    print("6. Cancel a task")
    print("7. Exit")

    choice = input("\nOption: ").strip()

    if choice == "1":
        add_task(content, notes_start, journal_file)

    elif choice == "2":
        completed_task(content, task_lines, journal_file)

    elif choice == "3":
        reopen_task(content, task_lines,journal_file)

    elif choice == "4":
        add_note(content, notes_start, journal_file)

    elif choice == "5":
        event = input("Enter a new event: ").strip()

        if not event:
            print("No event entered. Nothing was added.")
            continue

        event_line = f"- {event}\n"

        current_content = journal_file.read_text(encoding="utf-8")
        new_content = current_content.rstrip() + "\n" + event_line

        journal_file.write_text(
            new_content,
            encoding="utf-8"
        )

        print(f'Event added: "{event}"')

    elif choice == "6":
        cancel_task(content, task_lines, journal_file)

    elif choice == "7":
        print("Goodbye.")
        break

    else:
        print("Invalid option.")