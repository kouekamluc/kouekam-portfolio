release: npm ci && npm run build:css:prod && python manage.py collectstatic --noinput
web: gunicorn kouekam_hub.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 2 --timeout 120




