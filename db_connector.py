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
        # users_id INT IDENTITY(1,1) PRIMARY KEY NOT NULL: users_id is an identifier that represents the first column of the table,
        # it is the primary key, and it's not null, the (1,1) incrementing starting at 1 and increasing by 1 for each new row.
        # user_name VARCHAR(50) NOT NULL: stores user_name with a maximum variable-length string of 50 characters, NOT NULL insures that it has a value.
        # creation_date DATETIME DEFAULT GETDATE() VARCHAR(50):  stores creation_date with a maximum variable-length string of 50 characters,
        # DATETIME DEFAULT GETDATE() writes the date of the day!


            # Check if the table exists, and create it if it doesn't
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(50) NOT NULL,
                creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
                 );
            """)



        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        print(f"Connected successfully! {rows}")


        connection.commit() # The commit() method is used to make sure the changes made to the database.
        return connection, cursor
    
    # if it wasn't ablr to connect to the databse than it will returns an error:
    except pymysql.MySQLError as e:
        print(f"Connection failed: {e}")
        return None, None
