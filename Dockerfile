# Python base image
FROM python:3.9-slim

# Create a directory for the app
RUN mkdir /app

# Copy requirements.txt to the app directory
COPY requirements.txt /app

# Update pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the code to the app directory
COPY app/ /app

# Remove the storage directory
RUN rm -rf /app/storage/*

# Expose the port
EXPOSE 3000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
