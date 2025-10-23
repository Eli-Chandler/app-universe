import sqlite3

from app_universe.utils.diff_database import diff_databases


def _setup_schema(conn: sqlite3.Connection):
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE users (
            id   INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age  INTEGER NOT NULL,
            city TEXT
        );

        CREATE TABLE orders (
            id      INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            total   REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )
    conn.commit()


def _seed_original(conn: sqlite3.Connection):
    conn.executemany(
        "INSERT INTO users(id, name, age, city) VALUES(?, ?, ?, ?);",
        [
            (1, "Ana", 30, "NY"),
            (2, "Bob", 25, "SF"),
            (3, "Cara", 28, "LA"),
        ],
    )
    conn.executemany(
        "INSERT INTO orders(id, user_id, total) VALUES(?, ?, ?);",
        [
            (1, 1, 10.0),
            (2, 2, 20.0),
        ],
    )
    conn.commit()


def _seed_modified_from_scratch(conn: sqlite3.Connection):
    # Same base data as original...
    conn.executemany(
        "INSERT INTO users(id, name, age, city) VALUES(?, ?, ?, ?);",
        [
            (1, "Ana", 31, "NY"),  # UPDATED: age 30 -> 31
            (2, "Bob", 25, "SF"),  # UNCHANGED
            # (3, "Cara", 28, "LA"),  # REMOVED in modified
            (4, "Dan", 22, "SEA"),  # ADDED
        ],
    )
    conn.executemany(
        "INSERT INTO orders(id, user_id, total) VALUES(?, ?, ?);",
        [
            (1, 1, 10.0),  # unchanged table
            (2, 2, 20.0),
        ],
    )
    conn.commit()


def test_diff_databases_in_memory():
    # Create two independent in-memory DBs
    orig = sqlite3.connect(":memory:")
    mod = sqlite3.connect(":memory:")

    try:
        _setup_schema(orig)
        _setup_schema(mod)
        _seed_original(orig)
        _seed_modified_from_scratch(mod)

        diff = diff_databases(orig, mod)

        # Only 'users' changed; 'orders' should not be present
        assert set(diff.table_diffs.keys()) == {"users"}

        users_diff = diff.table_diffs["users"]

        # --- Added rows ---
        added_ids = {row["id"] for row in users_diff.added_rows}
        assert added_ids == {4}
        added_row_by_id = {row["id"]: row for row in users_diff.added_rows}
        assert added_row_by_id[4] == {"id": 4, "name": "Dan", "age": 22, "city": "SEA"}

        # --- Removed rows ---
        removed_ids = {row["id"] for row in users_diff.removed_rows}
        assert removed_ids == {3}
        removed_row_by_id = {row["id"]: row for row in users_diff.removed_rows}
        assert removed_row_by_id[3] == {"id": 3, "name": "Cara", "age": 28, "city": "LA"}

        # --- Updated rows ---
        # We expect only id=1 changed (age 30 -> 31)
        # updated_rows items are dicts like {"original_values": {...}, "modified_values": {...}}
        assert len(users_diff.updated_rows) == 1
        upd = users_diff.updated_rows[0]
        assert upd.original_values["id"] == 1
        assert upd.modified_values["id"] == 1
        assert upd.original_values["age"] == 30
        assert upd.modified_values["age"] == 31
        # Other fields unchanged
        assert upd.original_values["name"] == "Ana"
        assert upd.modified_values["name"] == "Ana"
        assert upd.original_values["city"] == "NY"
        assert upd.original_values["city"] == "NY"

    finally:
        orig.close()
        mod.close()
