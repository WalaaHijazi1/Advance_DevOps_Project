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
        # The function sends an HTTP GET request to the provided url using the requests library.
        response = requests.get(url, timeout=5)      # If the server doesn’t respond within 5 seconds, it raises an exception.

        if response.status_code == 200:     # If the response status code is 200, it means the request was successful, and the server responded properly. and then it will print a success message.
            print(f"Successfully stopped server: {url}")
        else:
            # If the status code is not 200, it means the request failed. It prints a failure message with the actual HTTP status code.
            print(f"Failed to stop server at {url}, status code: {response.status_code}")
            
    # Catches any request-related errors and prints a message indicating that the server might already be stopped or is not reachable.
    except requests.exceptions.RequestException as e:  
        print(f"Server at {url} may have already stopped or is unreachable: {e}")

# Calls stop_server() twice and Stop both backend and frontend servers
stop_server('http://127.0.0.1:5000/stop_server') # First, it tries to stop the backend server running on port 5000, for backend and combined testing.
#stop_server('http://127.0.0.1:5001/stop_server') # Then, it tries to stop the frontend server running on port 5001 for the frontend testing.


"""
The servers must have an endpoint (/stop_server) that handles the shutdown process.
When requests.get(url) is sent, the server is expected to shut itself down in response.
"""
