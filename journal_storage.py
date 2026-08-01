import shutil

from journal_parser import validate_journal_content

def write_journal(journal_file, content):
    if not validate_journal_content(content):
        print("Error: Refusing to write an invalid journal.")
        return False

    temporary_file = journal_file.with_suffix(
        journal_file.suffix + ".tmp"
    )

    backup_file = journal_file.with_suffix(
        journal_file.suffix + ".bak"
    )

    temporary_file.write_text(
        content,
        encoding="utf-8"
    )

    if journal_file.exists():
        shutil.copy2(
            journal_file,
            backup_file
        )

    temporary_file.replace(journal_file)

    return True

def replace_task(content, old_task, new_task, journal_file):
    new_content = content.replace(
        old_task,
        new_task,
        1
    )

    return write_journal(
        journal_file,
        new_content
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

    write_journal(
        journal_file,
        new_content
    )

def append_line(content, new_line, journal_file):
    new_content = content.rstrip() + "\n" + new_line

    write_journal(
        journal_file,
        new_content
    )

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