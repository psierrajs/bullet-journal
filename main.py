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

task = input("Enter a new task: ")

content = journal_file.read_text(encoding="utf-8")

tasks_header = "## Tasks\n"

task_line = f"- [ ] {task}\n"

tasks_start = content.find(tasks_header)

if tasks_start == 1:
    print("Error: Tasks section not found.")
else:
    insert_position = content.find("## Notes", tasks_start)

    if insert_position == -1:
        print("Error: Notes section not found.")
    else:
        before_notes = content[:insert_position].rstrip()
        after_notes = content[insert_position:]

        new_content = before_notes + "\n" + task_line + "\n" + after_notes

        journal_file.write_text(new_content, encoding="utf-8")

        print(f'Task added: "{task}"')




