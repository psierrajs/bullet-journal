from journal_storage import write_journal
from terminal_ui import pause, select_line

from bullet_journal.journal_parser import get_section_positions
from journal_storage import (
    append_line,
    insert_before_section,
    write_journal,
)
from terminal_ui import pause, select_line

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
