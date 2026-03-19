# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Render automatically provides the PORT environment variable)
ENV PORT=10000
EXPOSE $PORT

# Run the application using Gunicorn (1 worker is critical because we use APScheduler for Follow-Ups which would duplicate if multiple workers existed)
# Threads are set to 4 to handle concurrent web requests while background threads (threading.Thread) do the sending work.
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
