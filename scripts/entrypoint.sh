#!/bin/bash

set -e

echo "Ожидание готовности базы данных..."

echo "Запуск миграций Alembic..."
alembic upgrade head

echo "Запуск сервера FastAPI..."

exec "$@"
