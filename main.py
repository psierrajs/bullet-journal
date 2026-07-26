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
            "## Tasks \n\n"
            "## Notes\n\n"
            "## Events\n",
            encoding="utf-8"
		)

	print(f"Created journal: {journal_file}")
else:
	print(f"Journal already exists: {journal_file}")