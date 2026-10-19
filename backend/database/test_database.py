from database.connection import get_connection, close_connection, init_db
connection = get_connection()
try:
    cursor = connection.execute("SELECT id, name FROM accounts;")
    rows = cursor.fetchall()
    print(rows)
finally:
    close_connection(connection)