import sqlite3
import pandas as pd

def create_table(database_path, create_table_sql):
    """
    Create a table from the create_table_sql statement.
    :param database_path: a database file path.
    :param create_table_sql: a CREATE TABLE statement.
    """
    # Connect to the SQLite database
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Execute the SQL query to create a table
        cursor.execute(create_table_sql)
        print("Table created successfully.")
        
        # Commit the changes and close the database connection
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def insert_data_from_dataframe(database_path, table_name, dataframe):
    """
    Insert data from a DataFrame into an SQLite table.
    :param database_path: Path to the SQLite database.
    :param table_name: Name of the table to insert data into.
    :param dataframe: The pandas DataFrame containing the data.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    
    try:
        # Insert the data from the DataFrame into the SQLite table
        dataframe.to_sql(table_name, conn, if_exists='append', index=False)
        print("Data inserted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()
        
def drop_all_tables(database_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Retrieve all table names from the SQLite database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Drop each table
    for table_name in tables:
        drop_table_sql = f"DROP TABLE IF EXISTS {table_name[0]};"
        cursor.execute(drop_table_sql)
    
    # Commit the changes and close the database connection
    conn.commit()
    conn.close()
    print("All tables dropped successfully.")





