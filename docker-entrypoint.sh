#!/bin/bash
set -e

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head

# Run the command specified
exec "$@" 