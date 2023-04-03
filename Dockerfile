# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /code
WORKDIR /code

# Copy the requirements file into the container and install the dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /code
COPY . /code/

# Expose port 8000 for the Django application
EXPOSE 8000

# Run the command to start the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
