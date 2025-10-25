import sqlite3

from fastmcp import Client

from app_universe.utils.diff_database import AppUniverseDiff, DatabaseDiff

# TODO: This doesn't actually work, this is just a reminder to myself on how I'm planning on doing this

# I will either put these in a variable or a yaml file, not sure yet
"""
Name: Create comment
Prompt: Find the latest note and add a comment to it.
"""

def prepare_data(db_connections: dict[str, sqlite3.Connection]):
    pass

def evaluate_solution(diff: AppUniverseDiff) -> bool:
    assert diff.database_diffs.keys() == set()

    return True

async def golden_solution(prompt: str, mcp_servers: dict[str, Client]) -> str:
    return "All done."
