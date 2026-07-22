#!/bin/sh
set -eu

python manage.py migrate --noinput

if [ "${JIQING_SEED_DEMO:-false}" = "true" ]; then
  if [ -z "${JIQING_DEMO_PASSWORD:-}" ]; then
    echo "JIQING_SEED_DEMO=true 时必须设置 JIQING_DEMO_PASSWORD" >&2
    exit 1
  fi
  python manage.py seed_demo_data
fi

exec gunicorn jiqing_backend.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile -
