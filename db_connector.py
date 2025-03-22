import pymysql


def connect_data_table():
    # Connection details
    
    host="database-1.chaa2wuo8m7y.us-east-1.rds.amazonaws.com"
    port=3306
    dbname="users_data"
    user="adminwalaa"
    password="Walaa2511"


    try:
        # Connect to AWS database
        connection = pymysql.connect(host=host,
                      user = user,
                      port = port,
                      passwd = password,
                      database = dbname)

        cursor = connection.cursor() # Create a cursor object to interact with the database using the cursor() method, a cursor is a conceptual object
                                # that can be set as aan iterator.
       
        # The next command execute SQL queries using the execute() method of the cursor object.
        # it checks if a table exist in the database, if it doesn't it creates one by the name 'users'
        # INFORMATION_SCHEMA is a system databases that exists by default and contains all the information of the databases.
        #if the table doesn't exist it creates one with the name 'users', with the following details:
        # users_id INT PRIMARY KEY NOT NULL: users_id is an identifier that represents the first column of the table,
        # it is the primary key, and it's not null.
        # user_name VARCHAR(50) NOT NULL: stores user_name with a maximum variable-length string of 50 characters, NOT NULL insures that it has a value.
        # creation_date DATETIME DEFAULT GETDATE() VARCHAR(50):  stores creation_date with a maximum variable-length string of 50 characters,
        # DATETIME DEFAULT GETDATE() writes the date of the day!


        # Check if the table exists, and create it if it doesn't
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
                user_name VARCHAR(50) NOT NULL,
                creation_date DATETIME DEFAULT VARCHAR(50) CURRENT_TIMESTAMP
                 );
            """)



        cursor.execute("SELECT * FROM users") # here we fetch all the data from users database table.
        rows = cursor.fetchall()              # rows is a list of tuples, where each tuple represents a row from the users table.
        print(f"Connected successfully! {rows}")


        connection.commit() # The commit() method is used to make sure the changes made to the database.
        
        # connection: This represents the database connection object, It is used to interact with the database.
        # This is an object that allows you to execute SQL commands on the database. It is used to fetch, insert, update, or delete records.
        return connection, cursor
    
    # if it wasn't able to connect to the databse then it will returns an error:
    except pymysql.MySQLError as e:
        print(f"Connection failed: {e}")
        return None, None
