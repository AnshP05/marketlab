from database.connection import get_connection, close_connection

def list_accounts():
    connection  = get_connection()
    try:
        cursor = connection.execute("SELECT id, name FROM accounts;")
        accounts = cursor.fetchall()
        accounts_records = []
        for account_id, account_name in accounts:
            accounts_records.append({"id" : account_id, "name" : account_name})
        return accounts_records
    finally:
        close_connection(connection)

def open_account(account_name):
    connection = get_connection()
    try:
        sql = """INSERT INTO accounts (name) VALUES (?);"""
        cursor = connection.execute(sql, (account_name,))
        connection.commit()
        return cursor.lastrowid

    finally:
        close_connection(connection)