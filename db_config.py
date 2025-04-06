import mysql.connector

def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='yourpassword',
            database='book_exchange'
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None