#!/usr/bin/env bash
# Временные сертификаты для первого запуска nginx (браузер покажет предупреждение).
# Домен: аргумент $1, или переменная NGINX_SERVER_NAME, или admin.pmmeetup.pro.
# При смене домена: снова запустите скрипт (удалите ssl/*.pem) или замените на Let's Encrypt.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSL_DIR="$ROOT/ssl"
DOMAIN="${1:-${NGINX_SERVER_NAME:-admin.pmmeetup.pro}}"

mkdir -p "$SSL_DIR"
if [[ -f "$SSL_DIR/fullchain.pem" && -f "$SSL_DIR/privkey.pem" ]]; then
  echo "Уже есть $SSL_DIR/fullchain.pem и privkey.pem — удалите их вручную, чтобы пересоздать."
  exit 0
fi

openssl req -x509 -nodes -newkey rsa:2048 -days 90 \
  -keyout "$SSL_DIR/privkey.pem" \
  -out "$SSL_DIR/fullchain.pem" \
  -subj "/CN=${DOMAIN}/O=PM Meetup"

echo "Готово: $SSL_DIR/fullchain.pem, privkey.pem (self-signed, CN=$DOMAIN)"
