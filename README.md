#                    ˜”*°•.˜”*°• Advance DevOps Project •°*”˜.•°*”˜
#                          ˜”*°•.˜”*°• Walaa Hijazi •°*”˜.•°*”˜

The project was devided into parts:

## First Part:
I built a frontend and backend stack using python, General diagram of the this part:
<p align="center">
  <img src="images/GeneralDiagram.png" alt="General Diagram" width="650" height="600">
</p>

The rest_app.py file represents the backend server of the application.
It exposes a RESTful API that listens on port 5000 and handles HTTP requests at the endpoint:
#### http://127.0.0.1:5000/users/<USER_ID>
Clients can interact with it using the following HTTP methods:<br>
POST - Add a new user.<br>
GET - Retrieve user information by ID.<br>
PUT - Update an existing user's name.<br>
DELETE - Remove a user from the database.<br> 
Each request expects or returns JSON data, and the server interacts with a MySQL database to persist user data.<br>
