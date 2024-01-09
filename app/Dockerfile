# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory
WORKDIR /code

# Set environment variable to prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Add Debian repository for additional packages
RUN echo "deb https://deb.debian.org/debian/ stable main" > /etc/apt/sources.list

# Install necessary system packages
RUN apt-get update \
    && apt-get -y install libpq-dev swig vim gcc libssl-dev

# Copy and install Python dependencies
COPY requirements.txt /code/app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/app/requirements.txt

# Copy the application code
COPY . /code/app

# Set the default command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
