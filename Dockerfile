# Use an official Ubuntu base image
FROM ubuntu:22.04

# Set non-interactive mode to avoid prompts during the build
ENV DEBIAN_FRONTEND=noninteractive

# Remove broken cleanup hook
RUN rm -f /etc/apt/apt.conf.d/docker-clean

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.10 \
        python3-pip \
        python3.10-venv \
        tesseract-ocr \
        libgl1-mesa-glx \
        poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the Flask app's port
EXPOSE 5000

# Run the Flask app
CMD ["python3", "app.py"]
