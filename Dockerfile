# First stage: Install Python dependencies
FROM python:3.9-slim AS builder

WORKDIR /app

COPY app.py requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Second stage: Create final image with installed dependencies
FROM python:3.9-slim

WORKDIR /app

# Copy installed Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the rest of the application files
COPY app.py .

# Run the script when the container launches
CMD ["python", "app.py"]
