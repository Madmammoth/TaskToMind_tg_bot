#!/bin/sh
set -e

export PATH="/.venv/bin:$PATH"

echo "Waiting for PostgreSQL..."
python - <<EOF
import os, socket, time

host = os.getenv("POSTGRES_HOST", "postgres")
port = int(os.getenv("POSTGRES_PORT", 5432))

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except OSError:
        time.sleep(1)
EOF

echo "Waiting for Redis..."
python - <<EOF
import redis, os, time

r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ.get("REDIS_PASSWORD")
)

while True:
    try:
        r.ping()
        break
    except Exception:
        time.sleep(1)
EOF

echo "Applying migrations..."
python -m alembic upgrade head

echo "Starting bot..."
exec python main.py