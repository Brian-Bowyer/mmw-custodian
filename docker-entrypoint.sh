#!/bin/bash
alembic upgrade head && echo "DB migrated"
python3 -m app.main