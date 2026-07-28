from pathlib import Path
from datetime import date

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

content = journal_file.read_text(encoding="utf-8")

tasks_header = "## Tasks\n"
notes_header = "## Notes"

tasks_start = content.find(tasks_header)
notes_start = content.find(notes_header, tasks_start)

if tasks_start == -1:
    print("Error: Tasks section not found.")

elif notes_start == -1:
    print("Error: Notes section not found.")

else: 
    tasks_section = content[
        tasks_start + len(tasks_header): notes_start
    ]

    task_lines = []

    for line in tasks_section.splitlines():
        if line.startswith("- ["):
            task_lines.append(line)

    print("\nToday's tasks:\n")

    if not task_lines:
        print("No tasks yet.")
    else:
        for number, task_line in enumerate(task_lines, start=1):
            print(f"{number}. {task_line}")

    task = input("\nEnter a new task: ").strip()

    if not task:
        print("No task entered. Nothing was added.")
    else:
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






