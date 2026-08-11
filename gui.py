import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from datetime import date, timedelta
from pathlib import Path

from bullet_journal.journal_parser import (
    get_section_lines,
    get_section_positions,
    get_task_lines,
)
from bullet_journal.journal_storage import (
    create_daily_journal,
    insert_before_section,
    replace_task,
    write_journal,
)
from bullet_journal.version import __version__

from bullet_journal.journal_queries import (
    get_pending_tasks,
    search_journal_files,
)

from bullet_journal.gui_helpers import (
    get_journal_status,
    refresh_journal_status,
)

from gui_task_actions import (
    add_task_gui,
    cancel_task_gui,
    complete_task_gui,
    delete_task_gui,
    edit_task_gui,
    fill_task_section,
    get_task_summary,
    migrate_task_gui,
    refresh_tasks,
    reopen_task_gui,
)

from gui_note_actions import (
    add_note_gui,
    delete_note_gui,
    edit_note_gui,
    fill_note_section,
    refresh_notes,
)

from gui_event_actions import (
    add_event_gui,
    delete_event_gui,
    edit_event_gui,
    fill_event_section,
    refresh_events,
)

from bullet_journal.journal_queries import (
    get_journal_dates,
    get_pending_tasks,
    search_journal_files,
)

from bullet_journal.gui_backup_actions import (
    restore_backup_gui,
)

def load_journal(journal_date):
    journal_folder = Path("journal")
    journal_folder.mkdir(exist_ok=True)

    journal_file = (
        journal_folder
        / f"{journal_date.isoformat()}.md"
    )

    if not journal_file.exists():
        return (
            journal_date,
            journal_file,
            [],
            [],
            [],
        )

    content = journal_file.read_text(
        encoding="utf-8"
    )

    section_positions = get_section_positions(
        content
    )

    if section_positions is None:
        raise ValueError(
            "Invalid journal structure."
        )

    (
        tasks_start,
        notes_start,
        events_start,
    ) = section_positions

    task_lines = get_task_lines(content)

    if task_lines is None:
        raise ValueError(
            "Invalid journal structure."
        )

    note_lines = get_section_lines(
        content,
        notes_start,
        events_start,
    )

    event_lines = get_section_lines(
        content,
        events_start,
    )

    return (
        journal_date,
        journal_file,
        task_lines,
        note_lines,
        event_lines,
    )


def fill_section(frame, lines):
    for widget in frame.winfo_children():
        widget.destroy()

    if not lines:
        ttk.Label(
            frame,
            text="No entries yet.",
        ).pack(anchor="w")
        return

    for line in lines:
        ttk.Label(
            frame,
            text=line,
        ).pack(anchor="w", pady=2)


def create_section(parent, title):
    frame = ttk.LabelFrame(
        parent,
        text=title,
        padding=10,
    )
    frame.pack(
        fill="x",
        pady=(0, 10),
    )

    return frame


def open_journal_date(root, journal_date):
    root.destroy()
    main(journal_date)

def go_to_date_gui(root):
    date_text = simpledialog.askstring(
        "Go to date",
        "Enter date (YYYY-MM-DD):",
        parent=root,
    )

    if not date_text:
        return

    try:
        target_date = date.fromisoformat(
            date_text.strip()
        )
    except ValueError:
        messagebox.showerror(
            "Invalid date",
            "Please enter the date as YYYY-MM-DD.",
            parent=root,
        )
        return

    open_journal_date(
        root,
        target_date,
    )


def search_journals_gui(
    root,
    journal_folder,
    load_date_callback,
):
    search_window = tk.Toplevel(root)
    search_window.title("Search Journals")
    search_window.geometry("750x450")
    search_window.transient(root)

    search_frame = ttk.Frame(
        search_window,
        padding=15,
    )
    search_frame.pack(
        fill="both",
        expand=True,
    )

    ttk.Label(
        search_frame,
        text="Search journals",
        font=("Helvetica", 18, "bold"),
    ).pack(
        anchor="w",
        pady=(0, 10),
    )

    search_entry = ttk.Entry(
        search_frame,
    )
    search_entry.pack(
        fill="x",
        pady=(0, 10),
    )

    result_frame = ttk.Frame(
        search_frame
    )
    result_frame.pack(
        fill="both",
        expand=True,
    )

    columns = (
        "date",
        "line",
        "content",
    )

    result_tree = ttk.Treeview(
        result_frame,
        columns=columns,
        show="headings",
        selectmode="browse",
    )

    result_tree.heading(
        "date",
        text="Date",
    )

    result_tree.heading(
        "line",
        text="Line",
    )

    result_tree.heading(
        "content",
        text="Match",
    )

    result_tree.column(
        "date",
        width=110,
        stretch=False,
    )

    result_tree.column(
        "line",
        width=60,
        stretch=False,
    )

    result_tree.column(
        "content",
        width=500,
    )

    result_scrollbar = ttk.Scrollbar(
        result_frame,
        orient="vertical",
        command=result_tree.yview,
    )

    result_tree.configure(
        yscrollcommand=result_scrollbar.set
    )

    result_tree.pack(
        side="left",
        fill="both",
        expand=True,
    )

    result_scrollbar.pack(
        side="right",
        fill="y",
    )

    status_var = tk.StringVar(
        value="Enter text to search."
    )

    ttk.Label(
        search_frame,
        textvariable=status_var,
    ).pack(
        anchor="w",
        pady=(10, 0),
    )

    def run_search():
        search_text = search_entry.get().strip()

        for item in result_tree.get_children():
            result_tree.delete(item)

        if not search_text:
            status_var.set(
                "Enter text to search."
            )
            return

        results = search_journal_files(
            journal_folder,
            search_text,
        )

        for (
            journal_date,
            line_number,
            line,
        ) in results:
            result_tree.insert(
                "",
                "end",
                values=(
                    journal_date,
                    line_number,
                    line,
                ),
            )

        if results:
            status_var.set(
                f"{len(results)} match(es) found."
            )
        else:
            status_var.set(
                "No matches found."
            )

    def open_selected_result():
        selected = result_tree.selection()

        if not selected:
            return

        values = result_tree.item(
            selected[0],
            "values",
        )

        journal_date = date.fromisoformat(
            values[0]
        )

        load_date_callback(
            journal_date
        )

        search_window.destroy()

    button_frame = ttk.Frame(
        search_frame
    )

    button_frame.pack(
        fill="x",
        pady=(10, 0),
    )

    ttk.Button(
        button_frame,
        text="Search",
        command=run_search,
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        button_frame,
        text="Open Selected",
        command=open_selected_result,
    ).pack(side="left")

    search_entry.bind(
        "<Return>",
        lambda event: run_search(),
    )

    result_tree.bind(
        "<Double-1>",
        lambda event: open_selected_result(),
    )

    search_entry.focus_set()


def pending_tasks_gui(
    root,
    journal_folder,
    load_date_callback,
):
    pending_window = tk.Toplevel(root)
    pending_window.title("Pending Tasks")
    pending_window.geometry("700x450")
    pending_window.transient(root)

    main_frame = ttk.Frame(
        pending_window,
        padding=15,
    )
    main_frame.pack(
        fill="both",
        expand=True,
    )

    ttk.Label(
        main_frame,
        text="Pending Tasks",
        font=("Helvetica", 18, "bold"),
    ).pack(
        anchor="w",
        pady=(0, 10),
    )

    pending_tasks = get_pending_tasks(
        journal_folder
    )

    columns = (
        "date",
        "task",
    )

    task_tree = ttk.Treeview(
        main_frame,
        columns=columns,
        show="headings",
        selectmode="browse",
    )

    task_tree.heading(
        "date",
        text="Date",
    )

    task_tree.heading(
        "task",
        text="Task",
    )

    task_tree.column(
        "date",
        width=120,
        stretch=False,
    )

    task_tree.column(
        "task",
        width=500,
    )

    scrollbar = ttk.Scrollbar(
        main_frame,
        orient="vertical",
        command=task_tree.yview,
    )

    task_tree.configure(
        yscrollcommand=scrollbar.set
    )

    task_tree.pack(
        side="left",
        fill="both",
        expand=True,
    )

    scrollbar.pack(
        side="right",
        fill="y",
    )

    for (
        journal_date,
        task_line,
    ) in pending_tasks:
        task_tree.insert(
            "",
            "end",
            values=(
                journal_date,
                task_line,
            ),
        )

    def open_selected_task():
        selected = task_tree.selection()

        if not selected:
            return

        values = task_tree.item(
            selected[0],
            "values",
        )

        journal_date = date.fromisoformat(
            values[0]
        )

        load_date_callback(
            journal_date
        )

        pending_window.destroy()

    task_tree.bind(
        "<Double-1>",
        lambda event: open_selected_task(),
    )

def list_journals_gui(
    root,
    journal_folder,
    load_date_callback,
):
    list_window = tk.Toplevel(root)
    list_window.title("Available Journals")
    list_window.geometry("500x450")
    list_window.transient(root)

    main_frame = ttk.Frame(
        list_window,
        padding=15,
    )
    main_frame.pack(
        fill="both",
        expand=True,
    )

    ttk.Label(
        main_frame,
        text="Available Journals",
        font=("Helvetica", 18, "bold"),
    ).pack(
        anchor="w",
        pady=(0, 10),
    )

    journal_dates = get_journal_dates(
        journal_folder
    )

    columns = (
        "date",
        "formatted",
    )

    journal_tree = ttk.Treeview(
        main_frame,
        columns=columns,
        show="headings",
        selectmode="browse",
    )

    journal_tree.heading(
        "date",
        text="Date",
    )

    journal_tree.heading(
        "formatted",
        text="Journal",
    )

    journal_tree.column(
        "date",
        width=120,
        stretch=False,
    )

    journal_tree.column(
        "formatted",
        width=300,
    )

    scrollbar = ttk.Scrollbar(
        main_frame,
        orient="vertical",
        command=journal_tree.yview,
    )

    journal_tree.configure(
        yscrollcommand=scrollbar.set
    )

    journal_tree.pack(
        side="left",
        fill="both",
        expand=True,
    )

    scrollbar.pack(
        side="right",
        fill="y",
    )

    for journal_date in journal_dates:
        journal_tree.insert(
            "",
            "end",
            values=(
                journal_date.isoformat(),
                journal_date.strftime(
                    "%A, %d %B %Y"
                ),
            ),
        )

    def open_selected_journal():
        selected = journal_tree.selection()

        if not selected:
            return

        values = journal_tree.item(
            selected[0],
            "values",
        )

        journal_date = date.fromisoformat(
            values[0]
        )

        load_date_callback(
            journal_date
        )

        list_window.destroy()

    journal_tree.bind(
        "<Double-1>",
        lambda event: open_selected_journal(),
    )

    ttk.Button(
        main_frame,
        text="Open Selected",
        command=open_selected_journal,
    ).pack(
        anchor="w",
        pady=(10, 0),
    )

def main(journal_date=None):
    if journal_date is None:
        journal_date = date.today()

    root = tk.Tk()
    root.title(f"Bullet Journal v{__version__}")
    root.geometry("900x850")

    (
        current_date,
        journal_file,
        task_lines,
        note_lines,
        event_lines,
    ) = load_journal(journal_date)

    state = {
        "date": current_date,
        "journal_file": journal_file,
    }

    container = ttk.Frame(root)
    container.pack(
        fill="both",
        expand=True,
    )

    canvas = tk.Canvas(
        container,
        highlightthickness=0,
    )

    scrollbar = ttk.Scrollbar(
        container,
        orient="vertical",
        command=canvas.yview,
    )

    canvas.configure(
        yscrollcommand=scrollbar.set,
    )

    scrollbar.pack(
        side="right",
        fill="y",
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True,
    )

    main_frame = ttk.Frame(
        canvas,
        padding=20,
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=main_frame,
        anchor="nw",
    )

    def update_scroll_region(event):
        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    def resize_content(event):
        canvas.itemconfigure(
            canvas_window,
            width=event.width,
        )

    main_frame.bind(
        "<Configure>",
        update_scroll_region,
    )

    canvas.bind(
        "<Configure>",
        resize_content,
    )

    def on_mousewheel(event):
        if event.delta > 0:
            canvas.yview_scroll(-1, "units")
        elif event.delta < 0:
            canvas.yview_scroll(1, "units")

    canvas.bind_all(
        "<MouseWheel>",
        on_mousewheel,
    )

    # -------------------------------------------------
    # Header
    # -------------------------------------------------

    ttk.Label(
        main_frame,
        text="Bullet Journal",
        font=("Helvetica", 24, "bold"),
    ).pack(anchor="w")

    date_var = tk.StringVar(
        value=current_date.strftime(
            "%A, %d %B %Y"
        )
    )

    ttk.Label(
        main_frame,
        textvariable=date_var,
    ).pack(
        anchor="w",
        pady=(0, 8),
    )

    journal_status_var = tk.StringVar(
        value=get_journal_status(journal_file)
    )

    ttk.Label(
        main_frame,
        textvariable=journal_status_var,
        font=("Helvetica", 11, "italic"),
    ).pack(
        anchor="w",
        pady=(0, 10),
    )

    # -------------------------------------------------
    # Navigation
    # -------------------------------------------------

    navigation_frame = ttk.Frame(main_frame)
    navigation_frame.pack(
        anchor="w",
        pady=(0, 20),
    )

    ttk.Button(
        navigation_frame,
        text="← Previous",
        command=lambda: load_date(
            state["date"] - timedelta(days=1)
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        navigation_frame,
        text="Today",
        command=lambda: load_date(
            date.today()
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        navigation_frame,
        text="Next →",
        command=lambda: load_date(
            state["date"] + timedelta(days=1)
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        navigation_frame,
        text="Go to Date",
        command=lambda: go_to_date(),
    ).pack(side="left")

    ttk.Button(
        navigation_frame,
        text="Search",
        command=lambda: search_journals_gui(
            root,
            Path("journal"),
            load_date,
        ),
    ).pack(
        side="left",
        padx=(8, 0),
    )

    ttk.Button(
        navigation_frame,
        text="Pending Tasks",
        command=lambda: pending_tasks_gui(
            root,
            Path("journal"),
            load_date,
        ),
    ).pack(
        side="left",
        padx=(8, 0),
    )

    ttk.Button(
        navigation_frame,
        text="Journals",
        command=lambda: list_journals_gui(
            root,
            Path("journal"),
            load_date,
        ),
    ).pack(
        side="left",
        padx=(8, 0),
    )


    # -------------------------------------------------
    # Tasks
    # -------------------------------------------------

    selected_task_var = tk.StringVar()

    task_frame = create_section(
        main_frame,
        "Tasks",
    )

    task_frame.journal_status_var = (
        journal_status_var
    )

    fill_task_section(
        task_frame,
        task_lines,
        selected_task_var,
    )

    task_summary_var = tk.StringVar(
        value=get_task_summary(task_lines)
    )

    task_frame.summary_var = task_summary_var

    summary_frame = ttk.Frame(
        main_frame,
        padding=(10, 8),
    )

    summary_frame.pack(
        fill="x",
        pady=(0, 10),
    )

    ttk.Label(
        summary_frame,
        text="Task Summary",
        font=("Helvetica", 14, "bold"),
    ).pack(anchor="w")

    ttk.Label(
        summary_frame,
        textvariable=task_summary_var,
        font=("Helvetica", 12),
    ).pack(
        anchor="w",
        pady=(4, 0),
    )

    ttk.Separator(
        summary_frame,
        orient="horizontal",
    ).pack(
        fill="x",
        pady=(8, 0),
    )

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(
        fill="x",
        pady=(0, 20),
    )

    primary_buttons = ttk.Frame(
        button_frame
    )

    primary_buttons.pack(
        anchor="w",
        pady=(0, 8),
    )

    status_buttons = ttk.Frame(
        button_frame
    )

    status_buttons.pack(anchor="w")

    ttk.Button(
        primary_buttons,
        text="Add Task",
        command=lambda: add_task_gui(
            root,
            state["journal_file"],
            task_frame,
            selected_task_var,
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        primary_buttons,
        text="Edit Task",
        command=lambda: edit_task_gui(
            root,
            state["journal_file"],
            task_frame,
            selected_task_var,
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        primary_buttons,
        text="Delete Task",
        command=lambda: delete_task_gui(
            root,
            state["journal_file"],
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left")

    ttk.Button(
        status_buttons,
        text="Complete",
        command=lambda: complete_task_gui(
            state["journal_file"],
            task_frame,
            selected_task_var,
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        status_buttons,
        text="Reopen",
        command=lambda: reopen_task_gui(
            state["journal_file"],
            task_frame,
            selected_task_var,
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        status_buttons,
        text="Cancel",
        command=lambda: cancel_task_gui(
            state["journal_file"],
            task_frame,
            selected_task_var,
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        status_buttons,
        text="Migrate",
        command=lambda: migrate_task_gui(
            root,
            state["journal_file"],
            task_frame,
            selected_task_var,
        ),
    ).pack(side="left")

    # -------------------------------------------------
    # Notes
    # -------------------------------------------------

    selected_note_var = tk.StringVar()

    note_frame = create_section(
        main_frame,
        "Notes",
    )

    note_frame.journal_status_var = (
        journal_status_var
    )

    fill_note_section(
        note_frame,
        note_lines,
        selected_note_var,
    )

    note_button_frame = ttk.Frame(
        main_frame
    )

    note_button_frame.pack(
        anchor="w",
        pady=(0, 20),
    )

    ttk.Button(
        note_button_frame,
        text="Add Note",
        command=lambda: add_note_gui(
            root,
            state["journal_file"],
            note_frame,
            selected_note_var,
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        note_button_frame,
        text="Edit Note",
        command=lambda: edit_note_gui(
            root,
            state["journal_file"],
            note_frame,
            selected_note_var,
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        note_button_frame,
        text="Delete Note",
        command=lambda: delete_note_gui(
            root,
            state["journal_file"],
            note_frame,
            selected_note_var,
        ),
    ).pack(side="left")

    # -------------------------------------------------
    # Events
    # -------------------------------------------------

    selected_event_var = tk.StringVar()

    event_frame = create_section(
        main_frame,
        "Events",
    )

    event_frame.journal_status_var = (
        journal_status_var
    )

    fill_event_section(
        event_frame,
        event_lines,
        selected_event_var,
    )

    event_button_frame = ttk.Frame(
        main_frame
    )

    event_button_frame.pack(
        anchor="w",
        pady=(0, 20),
    )

    ttk.Button(
        event_button_frame,
        text="Add Event",
        command=lambda: add_event_gui(
            root,
            state["journal_file"],
            event_frame,
            selected_event_var,
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        event_button_frame,
        text="Edit Event",
        command=lambda: edit_event_gui(
            root,
            state["journal_file"],
            event_frame,
            selected_event_var,
        ),
    ).pack(
        side="left",
        padx=(0, 8),
    )

    ttk.Button(
        event_button_frame,
        text="Delete Event",
        command=lambda: delete_event_gui(
            root,
            state["journal_file"],
            event_frame,
            selected_event_var,
        ),
    ).pack(side="left")

    # -------------------------------------------------
    # Journal actions
    # -------------------------------------------------

    journal_actions_frame = ttk.LabelFrame(
        main_frame,
        text="Journal Actions",
        padding=10,
    )

    journal_actions_frame.pack(
        fill="x",
        pady=(0, 20),
    )

    ttk.Button(
        journal_actions_frame,
        text="Restore Backup",
        command=lambda: restore_backup_gui(
            root,
            state["journal_file"],
            load_date,
        ),
    ).pack(
        anchor="w",
    )

    # -------------------------------------------------
    # Date loading
    # -------------------------------------------------

    def load_date(new_date):
        try:
            (
                loaded_date,
                loaded_file,
                loaded_tasks,
                loaded_notes,
                loaded_events,
            ) = load_journal(new_date)

        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Unable to open journal",
                (
                    "The journal could not be opened.\n\n"
                    f"{error}"
                ),
                parent=root,
            )
            return

        state["date"] = loaded_date
        state["journal_file"] = loaded_file

        date_var.set(
            loaded_date.strftime(
                "%A, %d %B %Y"
            )
        )

        journal_status_var.set(
            get_journal_status(
                loaded_file
            )
        )

        selected_task_var.set("")
        selected_note_var.set("")
        selected_event_var.set("")

        fill_task_section(
            task_frame,
            loaded_tasks,
            selected_task_var,
        )

        fill_note_section(
            note_frame,
            loaded_notes,
            selected_note_var,
        )

        fill_event_section(
            event_frame,
            loaded_events,
            selected_event_var,
        )

        task_summary_var.set(
            get_task_summary(
                loaded_tasks
            )
        )

        canvas.yview_moveto(0)


    def go_to_date():
        date_text = simpledialog.askstring(
            "Go to date",
            "Enter date (YYYY-MM-DD):",
            parent=root,
        )

        if not date_text:
            return

        try:
            target_date = date.fromisoformat(
                date_text.strip()
            )
        except ValueError:
            messagebox.showerror(
                "Invalid date",
                "Please enter the date as "
                "YYYY-MM-DD.",
                parent=root,
            )
            return

        load_date(target_date)
    def open_search(event=None):
        search_journals_gui(
            root,
            Path("journal"),
            load_date,
        )

    def go_previous_day(event=None):
        load_date(
            state["date"] - timedelta(days=1)
        )

    def go_next_day(event=None):
        load_date(
            state["date"] + timedelta(days=1)
        )

    root.bind("<Command-f>", open_search)
    root.bind("<Control-f>", open_search)

    root.bind(
        "<Command-Left>",
        go_previous_day,
    )
    root.bind(
        "<Control-Left>",
        go_previous_day,
    )

    root.bind(
        "<Command-Right>",
        go_next_day,
    )
    root.bind(
        "<Control-Right>",
        go_next_day,
    )

    root.mainloop()


if __name__ == "__main__":
    main()



