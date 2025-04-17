# Defining the base image.
FROM python:3.9-slim 

# setting the workind directory: /app inside the container.
WORKDIR /app

# Copying the files from the project directory that is used to activate the Flask server into the container's working directory.
COPY requirements.txt rest_app.py db_connector.py backend_testing.py ./

# Installing python packages from the requirenments.txt file.
RUN pip3 install --no-cache-dir -r requirements.txt

# Telling Docker that the container listens on port 5000.
EXPOSE 5000

# In the end, this runs the rest_app.py file in order to start the server.
CMD ["python3","rest_app.py"]
