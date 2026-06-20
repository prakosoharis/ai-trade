#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: ./scripts/restore_db.sh backups/file.sql"
  exit 1
fi

FILE="$1"
if [ ! -f "$FILE" ]; then
  echo "File not found: $FILE"
  exit 1
fi

echo "Restoring from: $FILE"
cat "$FILE" | docker compose exec -T postgres psql -U "${POSTGRES_USER:-airesearch}" "${POSTGRES_DB:-airesearch}"
echo "Restore complete."
