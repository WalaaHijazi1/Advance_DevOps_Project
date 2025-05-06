import pymysql
import os


def connect_data_table():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "restapp"),
            database=os.getenv("DB_NAME", "user_db")
        )
        cursor = connection.cursor()


        # Check if the table exists, and create it if it doesn't
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(50) NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 );
            """)


        cursor.execute("SELECT * FROM users")
        # Fetching all the dat in the table's database.
        rows = cursor.fetchall()
        print(f"Connected successfully! {rows}")


        connection.commit() # The commit() method is used to make sure the changes made to the database.


        return connection, cursor
    except pymysql.MySQLError as e:
        print(f"Connection failed: {e}")
        return None, None