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

def validate_journal_content(content):
    tasks_start = content.find("## Tasks")
    notes_start = content.find("## Notes")
    events_start = content.find("## Events")

    if tasks_start == -1:
        return False

    if notes_start == -1:
        return False

    if events_start == -1:
        return False

    return tasks_start < notes_start < events_start