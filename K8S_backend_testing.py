# -*- coding: utf-8 -*-
import requests
import datetime
import pymysql
from db_connector import connect_data_table
import sys

# === Load Service URL from Jenkins-generated file ===
try:
    with open("k8s_url.txt", "r") as file:
        base_url = file.read().strip()
except FileNotFoundError:
    print("Error: 'k8s_url.txt' file not found.")
    sys.exit(1)

if not base_url.startswith("http"):
    print(f"Error: Invalid URL loaded from file: {base_url}")
    sys.exit(1)

url = f"{base_url}/users"
print(f"Using backend URL: {url}")

# === Function to get last inserted user ID from MySQL ===
def get_last_inserted_user_id(user_name):
    connection, cursor = connect_data_table()
    if cursor is None:
        print("Error: Could not connect to the database.")
        return None

    try:
        query = "SELECT user_id FROM users WHERE user_name=%s ORDER BY user_id DESC LIMIT 1"
        cursor.execute(query, (user_name,))
        result = cursor.fetchone()
    except Exception as e:
        print(f"DB query failed: {e}")
        result = None
    finally:
        cursor.close()
        connection.close()

    if result:
        return result[0]
    else:
        print("No matching user found in database.")
        return None

# === Function to POST new user ===
def post_new_data():
    global new_data
    new_data = {
        'user_name': 'carl',
        'creation_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        response = requests.post(url, json=new_data, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Failed to reach the backend: {e}")
        sys.exit(1)

    print("POST Response Status:", response.status_code)
    print("Raw Response:", response.text)

    try:
        data_from_post = response.json()
        print("Parsed JSON:", data_from_post)
    except requests.exceptions.JSONDecodeError:
        print("Error: The response is not valid JSON.")
        sys.exit(1)

    assert response.status_code == 200, f"API Error! Status: {response.status_code}"
    print("POST test passed.")

# === Function to GET the same user ===
def get_endpoint():
    global new_data
    user_name = new_data['user_name']
    user_id = get_last_inserted_user_id(user_name)

    if not user_id:
        print("Cannot test GET endpoint: user_id not found.")
        sys.exit(1)

    try:
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
































'''
import requests
import datetime
import pymysql
from db_connector import connect_data_table

# Load service URL from file created by Jenkins (minikube service ... > k8s_url.txt)
with open("k8s_url.txt", "r") as file:
    base_url = file.read().strip()

url = f"{base_url}/users"

def get_last_inserted_user_id(user_name):
    connection, cursor = connect_data_table()
    if cursor is None:
        print("Error: Could not connect to DB.")
        return None

    query = "SELECT user_id FROM users WHERE user_name=%s ORDER BY user_id DESC LIMIT 1"
    cursor.execute(query, (user_name,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        return result[0]
    else:
        print("No matching user found.")
        return None

def post_new_data():
    global new_data
    new_data = {
        'user_name': 'carl',
        'creation_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    response = requests.post(url, json=new_data)

    print("Response Status Code:", response.status_code)
    print("Raw Response Content:", response.text)

    try:
        data_from_post = response.json()
        print("Response JSON:", data_from_post)
    except requests.exceptions.JSONDecodeError:
        print("Error: The response is not valid JSON.")
        return

    assert response.status_code == 200, f"API Error! Status Code: {response.status_code}, Response: {response.text}"
    print(f"POST test passed. Data: {data_from_post}")

def get_endpoint():
    global new_data
    user_name = new_data['user_name']
    user_id = get_last_inserted_user_id(user_name)

    headers = {'User-Agent': 'Mozilla/5.0'}
    get_response = requests.get(f"{url}/{user_id}", headers=headers)

    print(f"GET request returned status code {get_response.status_code}")
    print(f"Response Content: {get_response.text}")

    assert get_response.status_code == 200, f"Expected 200 but got {get_response.status_code}"
    data_response = get_response.json()
    print(f"GET test passed successfully! Data: {data_response}")

if __name__ == "__main__":
    post_new_data()
    get_endpoint()

'''