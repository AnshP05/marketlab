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