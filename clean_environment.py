import requests

"""
Each call from the frontend or the backend testing, a url is passed based on the port that is listened from (where the backend or frontend server is running),
for the frontend it listens from port 5000,
and for the backend it listens from port 5001.

The function sends an HTTP GET request to that URL.
If the server is running and correctly handling /stop_server, it should shut down.
If the server is not running or unreachable, the function will print an error message instead of crashing.
"""

def stop_server(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"successfully stopped server: {url}")
        else:
            print(f"failed to stop server at {url}, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error had occured and stopped the server: {e}")



# Stop both backend and frontend servers
requests.get('http://127.0.0.1:5000/stop_server')
requests.get('http://127.0.0.1:5001/stop_server')