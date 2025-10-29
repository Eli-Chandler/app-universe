import sqlite3
from app_universe.utils.diff_database import DatabaseDiff
from fastmcp import Client


def prepare_data(db_connections: dict[str, sqlite3.Connection]):
    raise NotImplementedError("This is a template function. Please implement the logic.")

def evaluate_solution(database_diffs: dict[str, DatabaseDiff]) -> bool:
    raise NotImplementedError("This is a template function. Please implement the logic.")

async def golden_solution(prompt: str, mcp_servers: dict[str, Client]) -> str:
    raise NotImplementedError("This is a template function. Please implement the logic.")