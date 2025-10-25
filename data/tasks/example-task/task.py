import sqlite3

from fastmcp import Client

from app_universe.utils.diff_database import DatabaseDiff

def prepare_data(db_connections: dict[str, sqlite3.Connection]):
    notes_db = db_connections["notes"]
    notes_db.execute("INSERT INTO notes (id, content) VALUES (1, 'This is the first note.');")

def evaluate_solution(database_diffs: dict[str, DatabaseDiff]) -> bool:
    # TODO: I'm realising this is meant to return True/False, but I'm using asserts, will decide what exactly I want to do later
    # I will make a cleaner way to do this later
    assert list(database_diffs.keys()) == ["notes"], "Expected changes only in the 'notes' database."
    notes_diff = database_diffs["notes"].table_diffs
    # I will make a cleaner way to do this later
    assert list(notes_diff.keys()) == ["comments"], "Expected changes only in the 'comments' table."

    comments_table_diff = notes_diff["comments"]
    assert len(comments_table_diff.updated_rows) == 0, "Expected no updated comments."
    assert len(comments_table_diff.removed_rows) == 0, "Expected no removed comments."
    assert len(comments_table_diff.added_rows) == 1, "Expected exactly one added comment."

    added_comment = comments_table_diff.added_rows[0]
    assert added_comment["note_id"] == 1, "The comment should be associated with note ID 1 (the latest note)."

    return True

async def golden_solution(prompt: str, mcp_servers: dict[str, Client]) -> str:
    raise NotImplementedError("This is a template function. Please implement the logic.")