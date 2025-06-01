# Dockerfile with intentional security issues for testing

# INTENTIONAL ISSUE: Using outdated base image
FROM python:3.9

# INTENTIONAL ISSUE: Running as root user
WORKDIR /app

# INTENTIONAL ISSUE: Copying entire directory including sensitive files
COPY . /app/

# INTENTIONAL ISSUE: Not pinning package versions in pip install
RUN pip install --no-cache-dir -r requirements.txt

# INTENTIONAL ISSUE: Exposing internal port without proper security
EXPOSE 8000

# INTENTIONAL ISSUE: Hardcoded environment variables
ENV DATABASE_URL=postgresql://admin:password123@localhost:5432/testdb
ENV SECRET_KEY=super-secret-key-123
ENV DEBUG=true

# INTENTIONAL ISSUE: Creating directories with overly permissive permissions
RUN mkdir -p /app/uploads && chmod 777 /app/uploads
RUN mkdir -p /app/logs && chmod 777 /app/logs

# INTENTIONAL ISSUE: Installing additional packages without version control
RUN pip install requests urllib3 PyYAML

# INTENTIONAL ISSUE: No health check
# INTENTIONAL ISSUE: Running application as root
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]