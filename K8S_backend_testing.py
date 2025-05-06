# -*- coding: utf-8 -*-
import requests
import datetime
import pymysql
import os
import sys

# === Force override for DB_HOST during K8s port-forwarded test ===
# This assumes port-forwarding to localhost:3306 is active.
# os.environ: is a dictionary like object that creates a environment variable for the current proccess
os.environ['DB_HOST'] = '127.0.0.1'

from db_connector import connect_data_table  # after setting env

# === Load Service URL from Jenkins-generated file ===
# Here I openned the k8s_url text file that was created in jenkins pipeline in a reading mode,
# in base_url is saved all the contents of k8s_url.txt, with removing whitespaces and new lines.
try:
    with open("k8s_url.txt", "r") as file:
        base_url = file.read().strip()
except FileNotFoundError:
    print("Error: 'k8s_url.txt' file not found.")
    sys.exit(1)

# the base_url should be: http://127.0.0.1:<port-number>
# it might give back an empt string or a file path oran invalid url
if not base_url.startswith("http"):
    print(f"Error: Invalid URL loaded from file: {base_url}")
    sys.exit(1)


url = f"{base_url}/users"
print(f"Using backend URL: {url}")

# === Function to get last inserted user ID from MySQL ===
def get_last_inserted_user_id(user_name):

    # connection: connect us to the sql database, where ever it is: sql-container, or cloud base sql table
    # cursor: is a control interface to perform operations in sql.
    connection, cursor = connect_data_table()
    if cursor is None:
        print("Error: Could not connect to the database.")
        return None

    try:
        # selecting the user_id column from users table, and then filtering the rows that only has user_name.
        # selecting the rows of the same name in descending order (from highest to lowest), and choosing the first row.
        query = "SELECT user_id FROM users WHERE user_name=%s ORDER BY user_id DESC LIMIT 1"
        cursor.execute(query, (user_name,))
        # retrieving one row from the data that has been fetched, it returns as tuple.
        result = cursor.fetchone()
    except Exception as e:
        print(f"DB query failed: {e}")
        result = None
    finally:
        # Closing the cursor object and the database connection.
        cursor.close()
        connection.close()

    if result:
        return result[0]
    else:
        print("No matching user found in database.")
        return None

# === Function to POST new user ===
# This function sends a POST request that is sent by the client (front end) and connects to the backend (where sql data) through a Flask server.
def post_new_data():
    global new_data
    # This is the dictionary that has all the data to send to the backend, the keys are the column's names of the table in sql.
    new_data = {
        'user_name': 'carl',
        'creation_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        # sending the post request to the url, it is sent as a Jason file, it fails if there was no response in 10 seconds.
        response = requests.post(url, json=new_data, timeout=10)
        
    # printing the error that might be created from network connection.
    except requests.exceptions.RequestException as e:
        print(f"Failed to reach the backend: {e}")
        sys.exit(1)
        
    # showing the status_code of the response from the backend.
    # response.text is the body of the response from the backend.
    print("POST Response Status:", response.status_code)
    print("Raw Response:", response.text)

    try:
        # getting the resonse as a jason file (a python dictionary).
        data_from_post = response.json()
        print("Parsed JSON:", data_from_post)
    except requests.exceptions.JSONDecodeError:
        print("Error: The response is not valid JSON.")
        sys.exit(1)
    
    # Here if the status code is not 200 (passed successfully) the assertion would fails and it will raise an assersion error.
    assert response.status_code == 200, f"API Error! Status: {response.status_code}"
    print("POST test passed.")

# === Function to GET the same user ===
# The next function sends a GET request from frontend (user) to backend using Flask server, in order to fetch and check that the new data 
# inserted by the POST request is inserted successfully.
def get_endpoint():
    # global allows me to transfer a variable defined before through out the code in different functions, without definning them from scratch.
    global new_data
    user_name = new_data['user_name']
    user_id = get_last_inserted_user_id(user_name)

    # raised if the the user id not found.
    if not user_id:
        print("Cannot test GET endpoint: user_id not found.")
        sys.exit(1)

    try:
        # sends a GET request to the url defined below, to the Fllask endpoint, if it doesn't respond in 10 seconds it will fail.
        get_response = requests.get(f"{url}/{user_id}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"GET request failed: {e}")
        sys.exit(1)

    print(f"GET Response Status: {get_response.status_code}")
    print(f"Response Content: {get_response.text}")

    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}"
    print("GET test passed.")

# === Run both tests ===
if __name__ == "__main__":
    post_new_data()
    get_endpoint()