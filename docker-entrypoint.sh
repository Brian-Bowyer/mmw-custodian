#!/bin/bash
echo "Waiting for postgres..."
alembic upgrade head
echo "DB migrated"
python3 -m app.main