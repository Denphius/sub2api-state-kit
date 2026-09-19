#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ -e .env ] || [ -L .env ]; then
  echo '.env already exists; keeping your current configuration.'
  exit 0
fi
command -v openssl >/dev/null 2>&1 || { echo 'Please install openssl first.' >&2; exit 1; }
umask 077
set -C
{
  printf '%s\n' 'COMPOSE_PROJECT_NAME=sub2api-state-kit' 'BIND_HOST=127.0.0.1' 'SERVER_PORT=8080' 'ADMIN_EMAIL=admin@example.com' 'TZ=Asia/Shanghai'
  for key in ADMIN_PASSWORD POSTGRES_PASSWORD REDIS_PASSWORD JWT_SECRET TOTP_ENCRYPTION_KEY; do
    value=$(openssl rand -hex 32)
    printf '%s=%s\n' "$key" "$value"
  done
} > .env
echo 'Created .env with unique random secrets (owner-only permissions).'
echo 'Edit .env to set your admin email and bind address before starting.'
echo 'Your generated administrator password is the ADMIN_PASSWORD value in .env.'
echo 'Then run: docker compose up -d --build'
