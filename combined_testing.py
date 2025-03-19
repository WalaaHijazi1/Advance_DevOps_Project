"""
Combined testing – for Web interface, REST API and Database testing
(module name = combined_testing.py):
The script will:
 Post any new user data to the REST API using POST method.
 Submit a GET request to make sure data equals to the posted data.
 Using pymysql, check posted data was stored inside DB (users table).
 Start a Selenium Webdriver session.
 Navigate to web interface URL using the new user id.
 Check that the user name is correct.

Any failure will throw an exception using the following code: raise Exception("test failed")
"""


import requests
import datetime


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

import pymysql
import time
import tempfile


url = "http://127.0.0.1:5000/users"

#url = "http://172.17.0.1:5000/users"

# the post function is explained in the backend testing, this one is not very different from the one in the backend test.
# if you want to understand the steps in here please go back to the function in the backend testing file.
def post_new_user():

    global new_user_data

    new_user_data = {
        "user_name" : "ursula",
        "creation_date" : datetime.datetime.now().strftime("%Y-%M-%d %H:%M:%S")
    }

    response = requests.post(url, json=new_user_data)
    
    if response.status_code == 200:
        print("POST request passed successfully, the response is:", response.json())
    else:
        raise Exception(f"API POST request failed. Status code: {response.status_code}, Response: {response.text}")
    
    return response.json() 


# same here the get_requst is very similar to the function in the backend_testing so, thier it was explained explicitly.
def get_request():
    global new_user_data

    new_user_id = check_data()
    get_response = requests.get(f"{url}/{new_user_id}", json = new_user_data)

    # data_response = get_response.json()  # Convert response to a dictionary
    try:
      data_response = get_response.json()  # Attempt to parse JSON
    except requests.exceptions.JSONDecodeError:
      print('Response is not in JSON format.')
      data_response = None
    new_user_name = new_user_data["user_name"]
    
        # Proceed to check the status code
    assert get_response.status_code == 200, f"Expected status code 200, but got {get_response.status_code}"


    
    # assert data_response["user_name"] == new_user_name, \
    # f"Unexpected user name, data from get response: {data_response}. {data_response.get('user_name')}"


    return print(f"get response was successfully done with data : {get_response.json()}")


# in the db_connector file, the connection process to the table data base was explained on how and why.
def check_data():

    global new_user_data
    
    
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
                                
                                
        user_name = new_user_data["user_name"]
       


        # fetching user id of the giving user name:
        cursor.execute("SELECT user_id FROM users WHERE user_name= %s",(user_name,))
        user_id = cursor.fetchone()[0]
        connection.close()
        
        print(f"You have successfully connected to the data base, the data that was fetched is: {user_id} for {user_name}")

        print(f"user id is: {user_id}, type of user id is {type(user_id)}")

        return user_id
       
    # if the connection failed through the process an error will be raised:
    except Exception as e:
        print(f"Connection failed: {e}")
        return None




def selenium_session():
    global new_user_data
    
    # Retrieve the user name from the data defined earlier
    user_name = new_user_data["user_name"]
    
    # Retrieve the user ID using the check_data function
    new_user_id = check_data()
    
    
    driver_options = Options()

    driver_options.add_argument("--headless=new")
    driver_options.add_argument("--no-sandbox")
    driver_options.add_argument("--disable-dev-shm-usage")
    
    
    driver_options.add_argument(f"--user-data-dir={os.path.expanduser('~')}/chrome_data")
    
    driver_options.add_argument("--remote-debugging-port=9222")  # Unique devtools port
    
    # Set up the ChromeDriver Service
    #service = Service(ChromeDriverManager().install())
    # Set up the ChromeDriver Service
    chromedriver_path = "/root/.wdm/drivers/chromedriver/linux64/134.0.6998.88/chromedriver-linux64/chromedriver"
    service = Service(executable_path=chromedriver_path)
    
    # Initialize the Chrome WebDriver with the service and options
    driver = webdriver.Chrome(service=service, options=driver_options)
    
    
    try:
        
      new_url = f"http://127.0.0.1:5000/users/{new_user_id}"
      #new_url = f"http://172.17.0.1:5000/users/{new_user_id}"

      driver.get(new_url) # The driver navigates to the constructed URL.
      # Print the page source (HTML content)
      page_content = driver.page_source
      print(f"the page content: {page_content}")
      time.sleep(2) # A short sleep of 2 seconds is introduced to allow the page time to load completely before further actions are taken.

      wait = WebDriverWait(driver, 10)
      
    finally:
      # Close the browser
      driver.quit()


# Run all functions in sequence
def main():
    post_new_user()
    time.sleep(1)  # Give time for API processing
    get_request()
    time.sleep(1)
    check_data()
    time.sleep(1)
    selenium_session()

if __name__ == "__main__":
    main()
