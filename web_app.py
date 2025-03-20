"""
Web interface (module name: web_app.py):
The Web interface will be: 127.0.0.1:5001/users/get_user_data/<USER_ID>
1. The web interface will return the user name of a given user id stored inside users table
(Please refer to Database section).
2. The user name of the user will be returned in an HTML format with a locator to simplify
testing.
3. In case the ID doesn’t exist return an error (in HTML format)
For example:
@app.route("/get_user_name")
def get_user_name(user_id):
user_name = get_user_name_from_db(user_id)
return "<H1 id='user'>" + user_name + "</H1>"

@app.route("/get_user_name")
def get_user_name(user_id):
user_name = get_user_name_from_db(user_id)
if user_name == None:
return "<H1 id='error'>" no such user: + user_id + "</H1>"
"""

from flask import Flask, jsonify
from db_connector import connect_data_table
import os
import signal
import requests

# creates a Flask application object — app — in the current Python module
app = Flask(__name__)


def get_user_name(user_id):
    # Fetch user_name from database, not from Flask function!
    conn, cursor = connect_data_table()
    cursor.execute("SELECT user_name FROM dbo.users WHERE users_id = ?", (user_id,))
    # Fetching data from table data:
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


@app.route("/users/get_user_data/<int:user_id>") #a Flask route decorator that maps a URL endpoint to a Python function in a web application.
def get_user_name(user_id):

    # sending user id to theget_user_name function and returning the user name:
    user_name = get_user_name(user_id)
    
    if user_name:
        return "<H1 id='user'>" + user_name + "</H1>"
    else:
        return f"<H1 id='error'>No such user: {user_id}</H1>"


"""   
How It Works
@app.route('/stop_server')

This defines a Flask route at /stop_server.
When a user or another program makes a GET request to http://127.0.0.1:5000/stop_server (or another port where the Flask app is running), this function gets executed.
os.getpid()

This retrieves the process ID (PID) of the currently running Flask application.
os.kill(os.getpid(), signal.CTRL_C_EVENT)

This sends a CTRL+C (SIGINT) signal to the process with the given PID.
This effectively stops the Flask server, simulating a manual CTRL+C keyboard interruption.
return 'Server stopped'

After killing the server process, this message would typically be returned.
However, since the server is being stopped, the message may not always be sent back to the client before termination.
"""


@app.route('/stop_server')
def stop_server():
    response = jsonify({"message": "Shutting down server..."})  # Prepare response
    response.status_code = 200
    print("Shutting down server...")  # Optional: Log before shutting down
    os.kill(os.getpid(), signal.SIGINT)  # Shut down AFTER responding
    return response  # Send response first

#@app.route('/stop_server')
#def stop_server():
#    os.kill(os.getpid(), signal.SIGINT) #SIGINT is the Unix equivalent of a Ctrl+C interrupt.
#    return 'Server stopped'


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)