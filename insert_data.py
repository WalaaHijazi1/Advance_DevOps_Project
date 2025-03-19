import pyodbc
import datetime


import pymysql



def connect_data_table():
    
    host="database-1.chaa2wuo8m7y.us-east-1.rds.amazonaws.com"
    port=3306
    dbname="users_data"
    user="adminwalaa"
    password="Walaa2511"



    connection = None

    # Connect to Azure SQL Database
    try:

        # Now we will connect to the AWS RDS Database using the command pymysql.connect with the Database details from above.
        # Then we store this value in the variable "connection"

        connection = pymysql.connect(host=host,
                      user = user,
                      port = port,
                      passwd = password,
                      database = dbname)
        
        # create a cursor  object
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
        print(f"Connection failed: {e}")

    finally:
        # Close the connection
        if connection:
            connection.close()
            print("Connection closed.")


connect_data_table()
