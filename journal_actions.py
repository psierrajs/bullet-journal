from datetime import date, timedelta

from bullet_journal.journal_parser import (
    get_section_positions,
    get_task_lines,
)
from bullet_journal.journal_storage import (
    insert_before_section,
    replace_task,
)
from bullet_journal.terminal_ui import pause, select_task
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