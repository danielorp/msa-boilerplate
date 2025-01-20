# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the FastAPI application code
COPY app.py .

# Install FastAPI and Uvicorn
RUN pip install fastapi uvicorn

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
