from dataclasses import dataclass
import sqlite3
from typing import Any, Tuple

SKIP_TABLES = {"sqlite_sequence", "sqlite_stat1", "sqlite_stat2", "sqlite_stat3", "sqlite_stat4"}

@dataclass(frozen=True)
class DatabaseDiff:
    table_diffs: dict[str, "TableDiff"]

@dataclass(frozen=True)
class TableDiff:
    added_rows: list[dict]
    removed_rows: list[dict]
    updated_rows: list["RowDiff"]  # each item: {"original_values": dict, "modified_values": dict}

@dataclass(frozen=True)
class RowDiff:
    original_values: dict
    modified_values: dict

def _get_tables(connection: sqlite3.Connection) -> list[str]:
    cursor = connection.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall() if row[0] not in SKIP_TABLES]

def _get_pk_columns(connection: sqlite3.Connection, table: str) -> list[str]:
    """
    Return PK columns in PK order (works for composite PKs).
    """
    cur = connection.execute(f"PRAGMA table_info({table});")
    cols = cur.fetchall()  # (cid, name, type, notnull, dflt_value, pk)
    pk_cols = [c[1] for c in sorted(cols, key=lambda r: r[5]) if c[5] > 0]
    if not pk_cols:
        raise ValueError(f"Table {table} has no PRIMARY KEY.")
    return pk_cols

def _fetch_all_as_dicts(connection: sqlite3.Connection, sql: str) -> list[dict]:
    cur = connection.execute(sql)
    names = [d[0] for d in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]

def _get_rows(connection: sqlite3.Connection, table: str) -> dict[Tuple[Any, ...], dict]:
    """
    Return all rows from `table`, keyed by the PRIMARY KEY tuple.
    If the PK is a single column, the key is still a 1-tuple for consistency.
    """
    pk_cols = _get_pk_columns(connection, table)
    rows = _fetch_all_as_dicts(connection, f"SELECT * FROM {table};")

    def key_of(r: dict) -> Tuple[Any, ...]:
        return tuple(r[c] for c in pk_cols)

    return {key_of(r): r for r in rows}

def diff_databases(original_db_connection: sqlite3.Connection,
                   modified_db_connection: sqlite3.Connection) -> DatabaseDiff:
    # Same schema/tables on both sides, so we can just read from one
    tables = _get_tables(original_db_connection)

    table_diffs: dict[str, TableDiff] = {}

    for table in tables:
        orig_rows = _get_rows(original_db_connection, table)
        mod_rows  = _get_rows(modified_db_connection, table)

        orig_keys = set(orig_rows.keys())
        mod_keys  = set(mod_rows.keys())

        added_keys   = mod_keys - orig_keys
        removed_keys = orig_keys - mod_keys
        common_keys  = orig_keys & mod_keys

        added_rows   = [mod_rows[k] for k in added_keys]
        removed_rows = [orig_rows[k] for k in removed_keys]

        updated_rows = []
        for k in common_keys:
            o = orig_rows[k]
            m = mod_rows[k]
            if o != m:
                updated_rows.append(RowDiff(original_values=o, modified_values=m))

        # Only include tables that actually changed (your "changed tables" shortcut)
        if added_rows or removed_rows or updated_rows:
            table_diffs[table] = TableDiff(
                added_rows=added_rows,
                removed_rows=removed_rows,
                updated_rows=updated_rows
            )

    return DatabaseDiff(table_diffs=table_diffs)
