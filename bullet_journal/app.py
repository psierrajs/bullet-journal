from datetime import date

from .version import __version__

from .paths import get_journal_directory

from .entry_actions import (
    add_event,
    add_note,
    delete_event,
    delete_note,
    edit_event,
    edit_note,
)
from .journal_actions import (
    list_journals,
    list_pending_tasks,
    review_previous_day,
    search_journals,
    view_journal,
)
from .journal_parser import (
    get_section_lines,
    get_section_positions,
    get_task_lines,
)
from .journal_storage import (
    create_daily_journal,
    restore_backup,
)
from .task_actions import (
    add_task,
    cancel_task,
    complete_task,
    delete_task,
    edit_task,
    migrate_task,
    reopen_task,
)
from .terminal_ui import (
    display_journal_details,
    display_menu,
    display_tasks,
)

def main():
    print(f"\nBullet Journal v{__version__}")
    today = date.today()
    filename = f"{today.isoformat()}.md"

    journal_folder = Path("journal")
    journal_folder.mkdir(
    parents=True,
    exist_ok=True,
)

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
        display_journal_details(
            note_lines,
            event_lines,
            content
        )
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