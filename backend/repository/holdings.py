from database.connection import get_connection, close_connection


def insert_opening_position_in_database(account_id: int, ticker: str, quantity: int):
    # Create the connection, execute the query to insert into the table of opening positions,
    # commit, and return the ID 
    connection = get_connection()
    try:
        sql = """
            INSERT INTO opening_positions (account_id, symbol, quantity_micros)
            VALUES (?, ?, ?)
        """
        cursor = connection.execute(sql, (account_id, ticker, quantity))
        connection.commit()
        return cursor.lastrowid
    except:
        raise
        
    finally:
        close_connection(connection)