from database.connection import get_connection, close_connection
from portfolio.models import Holding
from integrations.finnhub import fetch_quote


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

def list_opening_positions():
    #Create the connection, execute the query and return it
    connection = get_connection()
    try:
        query = """
                SELECT
                    opening_positions.id,
                    opening_positions.account_id,
                    accounts.name,
                    opening_positions.symbol,
                    opening_positions.quantity_micros
                FROM opening_positions
                JOIN accounts
                    ON opening_positions.account_id = accounts.id
                ORDER BY opening_positions.account_id, opening_positions.id;
        """
        cursor = connection.execute(query)
        rows = cursor.fetchall()
        return rows
    finally:
        close_connection(connection)

def get_holding(position_id : int) -> Holding | None:
    connection = get_connection()
    try:
        query = """
                SELECT id, symbol, quantity_micros
                FROM opening_positions
                WHERE id = ?
            """
        cursor = connection.execute(query, (position_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        holding = Holding(
                symbol = row[1],
                position_id = row[0],
                quantity_micros = row[2]
            )

        return holding

    finally:
        close_connection(connection)
