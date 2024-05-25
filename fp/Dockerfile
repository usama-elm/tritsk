# Import the slim image
FROM python:3.11-slim-bookworm

# Install curl and other dependencies
RUN apt-get update && apt-get install -y curl python3-pip openssl

# Create a directory for Poetry
RUN mkdir -p /opt/poetry && \
    python3 -m venv /opt/poetry

# Activate the virtual environment and install Poetry
RUN /opt/poetry/bin/pip install poetry

# Add Poetry to the PATH
ENV PATH="/opt/poetry/bin:${PATH}"

WORKDIR /app

# Copy only the files necessary for installing dependencies to cache this step
COPY pyproject.toml poetry.lock* /app/

# Disable virtualenv creation by poetry to install dependencies globally
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Generate JWT secret and set it as an environment variable
RUN openssl rand -hex 32 | tee /app/JWT_SECRET.txt && \
    echo "JWT_SECRET=$(cat /app/JWT_SECRET.txt)" >> /etc/environment

# Load the environment variables
ENV $(cat /etc/environment)

# Copy the rest of the application
COPY . /app

CMD ["litestar", "--app", "api.main:app", "run", "--host", "0.0.0.0", "--port", "8897", "--debug"]
