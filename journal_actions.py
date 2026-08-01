from datetime import date

from journal_parser import get_task_lines
from terminal_ui import pause

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