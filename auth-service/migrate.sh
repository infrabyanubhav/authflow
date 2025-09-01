#!/bin/bash



set -e


trap 'echo "Error: Migration failed"' ERR

alembic upgrade head

echo "Migration completed successfully"



