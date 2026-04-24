#!/bin/sh
# Подставляет только NGINX_SERVER_NAME, чтобы не трогать $host и др. переменные nginx.
set -e
export NGINX_SERVER_NAME="${NGINX_SERVER_NAME:-admin.pmmeetup.pro}"
envsubst '${NGINX_SERVER_NAME}' </etc/nginx/default.conf.template >/etc/nginx/conf.d/default.conf
