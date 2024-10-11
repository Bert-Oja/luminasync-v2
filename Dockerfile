# Use an Alpine base image with Python 3.11.2
FROM python:3.11.2-alpine

# Install system dependencies and Poetry
RUN apk update && \
    apk add --no-cache git curl bash build-base && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="/root/.local/bin:$PATH"

# Set a working directory
WORKDIR /app

# Copy only the Poetry files to leverage caching
COPY pyproject.toml poetry.lock ./

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev

# Copy the rest of your application's code
COPY . .

# Expose port 5173
EXPOSE 5173

# Run the application with Python src/main.py
CMD ["python", "src/main.py"]
