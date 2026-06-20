#!/usr/bin/env bash
set -euo pipefail

mkdir -p backups
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
FILE="backups/airesearch-${TIMESTAMP}.sql"

echo "Creating backup: ${FILE}"
docker compose exec -T postgres pg_dump -U "${POSTGRES_USER:-airesearch}" "${POSTGRES_DB:-airesearch}" > "${FILE}"
echo "Backup complete: ${FILE}"
