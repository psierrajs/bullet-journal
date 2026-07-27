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

new_content = content.replace(
    tasks_header,
    f"{tasks_header}\n- [ ] {task}\n",
    1
)

journal_file.write_text(new_content, encoding="utf-8")

print(f'Task added: "{task}"')


