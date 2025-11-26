#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Dialogus..."

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
until redis-cli -h redis ping 2>/dev/null; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is ready!"

# Apply database migrations
echo "📦 Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
echo "👤 Creating superuser (if needed)..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@dialogus.com', 'admin123')
    print('Superuser created: username=admin, password=admin123')
else:
    print('Superuser already exists')
END

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || true

echo "✨ Starting Daphne ASGI server..."
# Execute the main command (daphne)
exec "$@"
