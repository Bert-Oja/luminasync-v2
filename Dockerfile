# Use an Alpine base image with Python 3.11.2
FROM python:3.11.2-alpine

# Install dependencies

RUN apk update && apk add --no-cache \
    git \
    build-base \
    gcc \
    g++ \
    make \
    cmake \
    libc-dev \
    musl-dev \
    linux-headers

# Set a working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . /app

# Compile the SCSS files to CSS using "python sass_compile.py"
RUN python sass_compile.py

# Expose port 5173
EXPOSE 5173

# Run the application with Python src/main.py
CMD ["python", "src/main.py"]
