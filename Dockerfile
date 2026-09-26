# Use the official Playwright Python image containing all necessary browser binaries
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python scripts and your Firebase security key
COPY bot.py .
COPY cloud_listener.py .
COPY serviceAccountKey.json .

# Start the cloud listener continuously
CMD ["python", "cloud_listener.py"]