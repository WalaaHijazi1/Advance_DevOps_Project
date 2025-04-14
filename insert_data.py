import datetime
import os

import pymysql

def connect_data_table():
    connection = None
    cursor = None
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "restapp"),
            database=os.getenv("DB_NAME", "restuser")
        )
        cursor = connection.cursor()
        # Create the users table if it doesn't exist
        create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(50) NOT NULL,
                creation_date VARCHAR(50) NOT NULL
            );
        """
        cursor.execute(create_table_query)
        print("Table 'users' created or already exists.")


        for _ in range(10):
            username = input("Enter user name to the data base: ")

            creation_date = datetime.datetime.now()

            cursor.execute("""INSERT INTO users (user_name,creation_date) VALUES (%s,%s)""", (username,creation_date))
        connection.commit()  # Save all inserts
        print("All users inserted successfully!")

        
    except Exception as e:
        print(f"Error connecting to database: {e}")

        
    finally:
        # Close the connection
        if connection:
            connection.close()
            print("Connection closed.")


connect_data_table()

