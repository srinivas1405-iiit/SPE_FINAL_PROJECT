# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install system dependencies (needed for some python packages)
# and upgrade pip, then install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Preload the model during build time (Cache this layer!)
COPY preload_model.py .
RUN python preload_model.py

# Copy the rest of the application code (frequent changes)
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the Flask app
CMD ["python", "SearchEngine_QA/searchES_FlaskAPI.py"]
