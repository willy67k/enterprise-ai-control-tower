# Use official Python image for the build and runtime
FROM python:3.11-slim-bookworm

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install dependencies first for better caching
# Copy only the files needed for installation
COPY pyproject.toml uv.lock ./

# Install dependencies without installing the project itself
# Using --frozen to ensure it matches the lockfile
RUN uv sync --frozen --no-cache --no-dev --no-install-project

# Copy application code
COPY . .

# Now install the project
RUN uv sync --frozen --no-cache --no-dev

# Expose backend port
EXPOSE 7801

# Run the application using the installed environment
# We use -m app.main which handles the uvicorn start as defined in the file
CMD ["uv", "run", "python", "-m", "app.main"]
