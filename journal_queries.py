from journal_parser import get_task_lines


def search_journal_files(
    journal_folder,
    search_text,
):
    results = []

    journal_files = sorted(
        journal_folder.glob("*.md")
    )

    for journal_file in journal_files:
        content = journal_file.read_text(
            encoding="utf-8"
        )

        for line_number, line in enumerate(
            content.splitlines(),
            start=1,
        ):
            if search_text.lower() in line.lower():
                results.append(
                    (
                        journal_file.stem,
                        line_number,
                        line,
                    )
                )

    return results


def get_pending_tasks(
    journal_folder,
):
    pending_tasks = []

    journal_files = sorted(
        journal_folder.glob("*.md")
    )

    for journal_file in journal_files:
        content = journal_file.read_text(
            encoding="utf-8"
        )

        task_lines = get_task_lines(content)

        if task_lines is None:
            continue

        for task_line in task_lines:
            if task_line.startswith("- [ ]"):
                pending_tasks.append(
                    (
                        journal_file.stem,
                        task_line,
                    )
                )

    return pending_tasks

