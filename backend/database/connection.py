from pathlib import Path
import sqlite3

#Creating the path objects so we don't have to write the full path everytime, and so we can run it from any directory
module_path = Path(__file__).resolve()
database_path = module_path.parent / "marketlab.db"


def get_connection():
    #creating the connection to the database
    connection = sqlite3.connect(database_path)

    #Each conennection needs foreign-key enabled so that 
    connection.execute("PRAGMA foreign_keys = ON")
    
    return connection

def close_connection(connection):
    connection.close()
    
def init_db():
    # Getting the paths to the schema and the actual SQL queries/tables into the txt
    schema_path = module_path.parent / "schema.sql"
    schema_txt = schema_path.read_text()
    # Creating a connection to marketlab.db creating the file if it doesn't exist
    connection = get_connection()
    try:
        connection.executescript(schema_txt)
        sql = "INSERT INTO accounts (name) VALUES (?);"
        connection.execute(sql, ("Wells Fargo",))
        connection.commit()
        
    finally:
        close_connection(connection)