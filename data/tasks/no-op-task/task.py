import sqlite3

from fastmcp import Client

from app_universe.utils.diff_database import AppUniverseDiff


def prepare_data(db_connections: dict[str, sqlite3.Connection]):
    pass

def evaluate_solution(diff: AppUniverseDiff) -> bool:
    assert diff.database_diffs.keys() == set()

    return True

def golden_solution(prompt: str, mcp_servers: dict[str, Client]) -> str:
    return "All done."
