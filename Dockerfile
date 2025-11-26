# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install Python dependencies first (cached layer)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/media /app/staticfiles

# Expose port
EXPOSE 8000

# Create entrypoint script inline to avoid line ending issues
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Starting Dialogus..."\n\
sleep 5\n\
python manage.py migrate --noinput\n\
python manage.py collectstatic --noinput || true\n\
exec daphne -b 0.0.0.0 -p 8000 chatproject.asgi:application' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
