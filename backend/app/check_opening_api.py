"""Run from backend: .venv/bin/python -m app.check_opening_api.

Send in-process HTTP requests through the ASGI app, using a temporary database.
No browser, server socket, or application database is used.
"""

import asyncio
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app.main import app
from repository import holdings


async def post_opening(payload):
    body = json.dumps(payload).encode()
    messages = []

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/holdings/opening",
        "raw_path": b"/api/v1/holdings/opening",
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-type", b"application/json"), (b"host", b"testserver")],
        "server": ("testserver", 80),
        "client": ("testclient", 1234),
    }
    await app(scope, receive, send)
    status = next(
        message["status"] for message in messages
        if message["type"] == "http.response.start"
    )
    content = b"".join(
        message.get("body", b"") for message in messages
        if message["type"] == "http.response.body"
    )
    return status, json.loads(content)


async def main():
    schema = Path(__file__).resolve().parents[1] / "database" / "schema.sql"
    with TemporaryDirectory() as directory:
        database = Path(directory) / "api-check.db"
        setup = sqlite3.connect(database)
        try:
            setup.executescript(schema.read_text())
            setup.execute(
                "INSERT INTO accounts (id, name) VALUES (?, ?)", (2, "Test account")
            )
            setup.commit()
        finally:
            setup.close()

        def temporary_connection():
            connection = sqlite3.connect(database)
            connection.execute("PRAGMA foreign_keys = ON")
            return connection

        payload = {"account_id": 2, "ticker": "AAPL", "quantity": "2.25"}
        with patch.object(holdings, "get_connection", temporary_connection):
            status, body = await post_opening(payload)
            assert status == 201, (status, body)
            position_id = body["position_id"]
            assert isinstance(position_id, int), body
            print("PASS: creation returns 201 and a named position ID.")

            cases = (
                ("duplicate", payload, 409, str),
                ("missing account", {**payload, "account_id": 999}, 404, str),
                ("invalid quantity", {**payload, "quantity": "abc"}, 422, str),
                ("missing field", {"account_id": 2, "ticker": "MSFT"}, 422, list),
            )
            for label, request, expected_status, detail_type in cases:
                status, body = await post_opening(request)
                assert status == expected_status, (label, status, body)
                assert isinstance(body["detail"], detail_type) and body["detail"], body
                print(f"PASS: {label} returns {status} with error detail.")

            failures = (
                sqlite3.OperationalError("Synthetic internal database diagnostic"),
                sqlite3.IntegrityError("Synthetic unexpected constraint diagnostic"),
            )
            failures[1].sqlite_errorcode = sqlite3.SQLITE_CONSTRAINT_CHECK
            for failure in failures:
                with patch.object(holdings, "get_connection", side_effect=failure):
                    status, body = await post_opening(payload)
                assert status == 500, (status, body)
                assert body == {"detail": "Unable to save the opening position."}, body
            print("PASS: other database/constraint failures return generic JSON 500.")

        reader = sqlite3.connect(database)
        try:
            rows = reader.execute(
                "SELECT id, account_id, symbol, quantity_micros FROM opening_positions"
            ).fetchall()
            assert rows == [(position_id, 2, "AAPL", 2250000)], rows
        finally:
            reader.close()
        print("PASS: exact saved quantity persists; rejected requests add no rows.")


if __name__ == "__main__":
    asyncio.run(main())
