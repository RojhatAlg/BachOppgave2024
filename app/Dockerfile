# Use the official Python image from Docker Hub
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Add a dummy instruction to invalidate cache
RUN echo "dummy"

# Copy the entire project directory into the container at /app
COPY . /app/

# Command to run the Python application
CMD ["python", "github-commits-detailed.py"]
