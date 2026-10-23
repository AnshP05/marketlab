"""Run from backend: .venv/bin/python -m repository.check_holdings.

Use a temporary database to check the service/repository without changing application data.
"""

from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from unittest.mock import patch

from repository import holdings
from portfolio import service
from portfolio.errors import InvalidQuantityError


def main():
    schema = Path(__file__).resolve().parents[1] / "database" / "schema.sql"
    opened_connections = []

    with TemporaryDirectory() as temporary_directory:
        database = Path(temporary_directory) / "holdings.db"
        setup = sqlite3.connect(database)
        try:
            setup.executescript(schema.read_text())
            setup.execute(
                "INSERT INTO accounts (id, name) VALUES (?, ?)",
                (2, "Test account"),
            )
            setup.commit()
        finally:
            setup.close()

        def temporary_connection():
            connection = sqlite3.connect(database)
            connection.execute("PRAGMA foreign_keys = ON")
            opened_connections.append(connection)
            return connection

        # Replace only the connection factory; exercise the actual repository.
        with patch.object(holdings, "get_connection", temporary_connection):
            position_id = service.open_holding(2, "AAPL", "2.25")
            assert isinstance(position_id, int), "Expected a created row ID"

            connection_count = len(opened_connections)
            try:
                service.open_holding(2, "INVALID", "abc")
            except InvalidQuantityError:
                pass
            else:
                raise AssertionError("Expected quantity error to propagate from service")
            assert len(opened_connections) == connection_count, "Invalid input reached database"

            rejected = (
                (2, "AAPL", 1000000),  # Duplicate account/ticker.
                (999, "MSFT", 1000000),  # Nonexistent account.
                (2, "ZERO", 0),
                (2, "NEGATIVE", -1),
            )
            for arguments in rejected:
                try:
                    holdings.insert_opening_position_in_database(*arguments)
                except sqlite3.IntegrityError:
                    continue
                raise AssertionError(f"Expected IntegrityError for {arguments!r}")

        # A separate connection proves that the successful write was committed.
        reader = sqlite3.connect(database)
        try:
            rows = reader.execute(
                "SELECT id, account_id, symbol, quantity_micros FROM opening_positions"
            ).fetchall()
            assert rows == [(position_id, 2, "AAPL", 2250000)], rows
        finally:
            reader.close()

        for connection in opened_connections:
            try:
                connection.execute("SELECT 1")
            except sqlite3.ProgrammingError:
                continue
            raise AssertionError("Repository left a connection open")

    print("PASS: service converts shares, saves the row, and returns its committed ID.")
    print("PASS: quantity errors propagate before a database connection is opened.")
    print("PASS: exact saved quantity survives reopening.")
    print("PASS: duplicate, missing account, zero, and negative quantity reject.")
    print("PASS: failed inserts leave no extra rows; all repository connections close.")


if __name__ == "__main__":
    main()
