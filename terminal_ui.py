from journal_parser import count_tasks_by_status

def display_tasks(task_lines):
    print("\nToday's tasks:\n")

    if not task_lines:
        print("No tasks yet.")
        return

    for number, task_line in enumerate(
        task_lines,
        start=1
    ):
        print(f"{number}. {task_line}")

def display_task_summary(content):
    counts = count_tasks_by_status(content)
    total = sum(counts.values())

    if total == 0:
        progress = 0
    else:
        progress = round(
            counts["completed"] / total * 100
        )

    print("\nTask summary:")
    print(f"Total: {total}")
    print(f"Open: {counts['open']}")
    print(f"Completed: {counts['completed']}")
    print(f"Cancelled: {counts['cancelled']}")
    print(f"Migrated: {counts['migrated']}")
    print(f"Progress: {progress}%")

def display_journal_details(
    note_lines,
    event_lines,
    journal_content
):
    display_task_summary(journal_content)

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
    print("7. Migrate a task")
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

    if (
        task_number < 1
        or task_number > len(task_lines)
    ):
        print("That task number does not exist.")
        return None

    return task_lines[task_number - 1]


def select_line(lines, prompt):
    if not lines:
        return None

    line_number_text = input(prompt).strip()

    if not line_number_text.isdigit():
        print("Please enter a valid number.")
        return None

    line_number = int(line_number_text)

    if (
        line_number < 1
        or line_number > len(lines)
    ):
        print("That number does not exist.")
        return None

    return lines[line_number - 1]


def pause():
    input("Press Enter to continue...")