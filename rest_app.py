from flask import Flask, request, jsonify
from db_connector import connect_data_table
import logging

import pymysql
from contextlib import closing



from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.debug = True


# Set up logging
file_handler = logging.FileHandler('error.log')
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)


import datetime
"""
POST – will accept user_name parameter inside the JSON payload.
A new user will be created in the database (Please refer to Database section) with the
id passed in the URL and with user_name passed in the request payload.
ID has to be unique!

On success: return JSON : {“status”: “ok”, “user_added”: <USER_NAME>} + code: 200
On error: return JSON : {“status”: “error”, “reason”: ”id already exists”} + code: 500
"""


@app.route('/')
def home():
    return 'Welcome To The Identification Page'

# @app.route is a Flask route decorator that tells Flask to execute the function below it whenever a POST request is sent to the /users endpoint.
@app.route('/users', methods=['POST'])
def post_method():

    data = request.get_json()  # extracting JSON data sent by the client in a POST request.

    if not data or 'user_name' not in data: # if user name was not passed in the data json file, then it will return an error
        return jsonify({'status': 'error', 'reason': 'missing user_name'}), 400

    user_name = data['user_name'] # extracting user name from the data json that is put in a dictionary

    print(f"The data: {data}, type of the data:{type(data)}") # printing to make sure everything is ok!
    user_added = add_user(user_name) # add the user into the table, taking the function from db.connector python file, where user name is added to the table.
    # and the id is added by the sql database, and another column which is creation date that is set up in the function.

    # the add_user function returns a true is the user was added, and false if the user is already exist, or there is a missing data in the data that was passed,
    # so user_added will return True if the user was added successfully or False if there was a specific Error.
    if user_added:
        # after adding the user, I wanted to make sure that the user does exist!
        # so I passed the user name in the function check_user_name.
        # The function will return True, if the user exist, and false if it doesn't exist.
        user_name_exist = check_user_name(user_name)
        if user_name_exist:
            return jsonify({'status': 'ok', 'user_added': user_name}), 200
        else:
            return jsonify({'status': 'error', 'reason': 'missing parameters'}), 400
    else:
            return jsonify({'status': 'error', 'reason': 'user already exist'}), 500


"""
2. GET – returns the user name stored in the database for a given user id.
Following the example: 127.0.0.1:5000/users/1 will return john.
On success: return JSON : {“status”: “ok”, “user_name”: <USER_NAME>} + code: 200
On error: return JSON : {“status”: “error”, “reason”: ”no such id”} + code: 500
"""

# here it will be executed if it was sent GET, PUT or DELETE request to the endpoint /users/<int:user_id>.
@app.route('/users/<int:user_id>', methods=["GET","PUT","DELETE"])
def get_data(user_id):
    # if the request that was passed is a GET one:
    if request.method == 'GET':
        # first we will check if the user's data already exist.
        # global user_exist
        # user_exist = users_data(user_id)
        if users_data(user_id): # the function users_data will return True if it does exist and flase if it doesn't.
            # call the get_user_name func and get the name of the user.
            user_name = get_user_name_from_db(user_id)
            if user_name:
                return jsonify({'status': 'ok', 'user_name': user_name}), 200
            else:
                return jsonify({'status': 'error', 'reason': 'user name not found'}), 404
            # if the user name was found in the user_id, it will return the message below with the status: ok 
            # and the user name of the user id, with a status code of 200 that means the request was successful 
            # The requested resource has been fetched and transmitted to the message body.
        else:
            # if it hasn't fetched the data, it returs an error with a message that it hasn't find an id of the user name.
            # with a status code of 500 which the server encountered an unexpected condition that prevented it from fulfilling the request.
            return jsonify({'status': 'error', 'reason': 'no such id'}), 500
        

        """
        3. PUT – will modify existing user name (in the database).
        Following the above example, when posting the below JSON payload to
        127.0.0.1:5000/users/1
        george will replace john under the id 1
        {“user_name”: “george”}
        On success: return JSON : {“status”: “ok”, “user_updated”: <USER_NAME>} + code: 200
        On error: return JSON : {“status”: “error”, “reason”: ”no such id”} + code: 500

"""

@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    # Handle non-HTTP exceptions
    return jsonify({'status': 'error', 'message': str(e)}), 500


    # if the request was a PUT one:
def put_request(user_id, new_user_name):
    if request.method == 'PUT':
        # from the begining we check if the user already exist or not:
        if user_exist:
            # The next line retrieves the JSON data sent in the HTTP request (PUT request) and parses it into a Python dictionary.
            # By default this function will return None if the mimetype is not application/json
            data = request.get_json() 
            new_user_name = {"user_name": "george"}
            # we retreive the user name that I want to replace:
            replace_user_name = data.get("user_name")
            # this function is in the db_connector that modefise the name
            # it takes the id and the user name that will be replaced, and finally the new user name.
            modify_name(user_id, replace_user_name["user_name"],new_user_name)
            return jsonify({'status': 'ok', 'user_name': replace_user_name["user_name"]}), 200
        else:
            # if it did not succeed in replacing the user name it will give back an error:
            return jsonify({'status': 'error', 'reason': 'no such id'}), 500

        """
        4. DELETE – will delete existing user (from database).
        Following the above (marked) example, when using delete on 127.0.0.1:5000/users/1
        The user under the id 1 will be deleted.
        On success: return JSON : {“status”: “ok”, “user_deleted”: <USER_ID>} + code: 200
        On error: return JSON : {“status”: “error”, “reason”: ”no such id”} + code: 500
        """

def delete_func(user_id):
    if request.method == 'DELETE': 
        # checking if the user exist:  
        if user_exist:
            # delete_name is a function in the db_Connector file,
            # it deletes the user that has the user_id that was passed to the func.
            name_deleted = delete_name(user_id)
            # the function above returns True if the name was deleted and false if it didn't.
            if name_deleted:
                return jsonify({"status": "ok", "user_deleted": user_id}), 200
            else:
                return jsonify({"status": "error", "reason": "no such id"}), 500


@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content response

# FUNCTIONS THAT I USED:
# the following functions checks if user exist in the data base or not

def users_data(user_id):

    conn, cursor = connect_data_table()
    # if there was an error in connecting to the DB.
    if not cursor:
        return None

    # Read data
    cursor.execute("SELECT user_id, user_name, creation_date FROM users")
    # Fetch all the dat in the data base.
    rows = cursor.fetchall()

    exist = False
    # iterate over the rows in the table and checks if the id that was given is in the table or not
    # returns True if user_id exist and False if it does not exist.
    for row in rows:
        print(row)
        if row[0] == user_id:
            exist = True
            print("The user does exist!!")
            break
    conn.commit()
    conn.close()

    return exist




def add_user(user_name):
    # connect to the database in the cloud.
    # the try-except method in here because if there would be a connection error.
    # or an error in the sql.
    try:
        conn, cursor = connect_data_table()
        if not cursor:
            return "Database connection failed"  # Handle connection failure
        

        # Insert new user (assuming user_id is auto-generated)
        cursor.execute("INSERT INTO users (user_name, creation_date) VALUES (%s, CURRENT_TIMESTAMP)", (user_name,))
        conn.commit()
        return True # if user was added successfully

    except Exception as e:
        print(f"Error: {e}")
        return False
    
    # finally, it will go to finally and execute the commands in it!
    finally:
        # if there was not an error it will be executed, but if there was an error it won't.
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# the following func checks if the user name is in the data base or not:
def check_user_name(user_name):
    try:
        # connect to the databse and it interacts with it:
        conn, cursor = connect_data_table()

        # now, it checks if the user name exist, using sql langauge
        cursor.execute("SELECT * FROM users WHERE user_name LIKE %s",(f"%{user_name}%",))
        # fetching the user name from database
        user = cursor.fetchone()
        # the next line returns True if the user has a user name and false if it doesn't
        return bool(user)
      
    except Exception as e:
        print("Error: ", e)
        return False
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# the next function modefies the name of an existing user name
def modify_name(user_id, user_name, new_user_name):
    try:
        # connect to the databse and it interacts with it:
        conn, cursor = connect_data_table()
    
        # here I check the user name and user id exist together.
        cursor.execute("SELECT * FROM users WHERE user_name = %s AND user_id = %s",(user_name,user_id))
        conn.commit()

        # here we fetch the result for db:
        result = cursor.fetchone()
        # then we found_user is True if result have data, if it has None that it is False.
        found_user = result is not None

        
        if found_user: # if the user does really exist:
            # Update the user_name where user_id matches
            cursor.execute("UPDATE users SET user_name = %s WHERE user_id = %s", (new_user_name, user_id))
            conn.commit()  # Save changes

    except pymysql.MySQLError as e:
        print("Error: ", e)
        return False
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# the nest function deletes user name:
def delete_name(user_id):
    try:
        # connect to the databse and it interacts with it:
        conn, cursor = connect_data_table()
        
        # navigate to the table and specifically to the user id that was passed by the user and delete the user name and id:
        cursor.execute("DELETE FROM users "
                        "WHERE user_id = %s",
                        (user_id,))
        # printing how many rows were deleted (it suppose to be always 1)
        print("Deleted", cursor.rowcount, "row(s) of data.")
        conn.commit()
        return cursor.rowcount > 0
    
    except pymysql.MySQLError as e:
        print("Error: ", e)
        return False
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# this function returns the user name that it's id would be passed:
def get_user_name_from_db(id_num):
    try:
        # connect to the databse and it interacts with it:
        conn, cursor = connect_data_table()

        # fetching the data from dbase and returning the user name with the specific id.
        cursor.execute("SELECT user_name FROM users WHERE user_id = %s",(id_num,))
        user_name = cursor.fetchone()[0]

        return user_name
    except Exception as e:
        print("Error: ", e)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' , port =5000)
