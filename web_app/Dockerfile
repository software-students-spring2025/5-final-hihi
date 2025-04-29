# web_app/Dockerfile

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir flask pymongo

# Expose Flask port
EXPOSE 5000

# Start the web app
CMD ["python", "front_end/app.py"]
