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

