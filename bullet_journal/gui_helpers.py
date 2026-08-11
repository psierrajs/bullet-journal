def get_journal_status(journal_file):
    if journal_file.exists():
        return "Journal exists"

    return (
        "No journal yet — "
        "it will be created when you add content"
    )


def refresh_journal_status(
    journal_file,
    frame,
):
    status_var = getattr(
        frame,
        "journal_status_var",
        None,
    )

    if status_var is not None:
        status_var.set(
            get_journal_status(
                journal_file
            )
        )

        