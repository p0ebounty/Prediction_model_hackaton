FROM python:3.10-slim

# Install system dependencies required by LightGBM and other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Ensure data files are accessible (assuming they are in the data/ folder)
# If they are large, consider other ways to provide them in a production environment

# The command to run your application
# Render will set the PORT environment variable
# We need to ensure uvicorn uses it and listens on 0.0.0.0
CMD ["python", "app/run_all.py"] 
