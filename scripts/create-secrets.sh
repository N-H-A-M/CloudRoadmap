#!/bin/bash

echo "Creating PostgreSQL Secret"

read -p "Postgres User: " PG_USER
read -sp "Postgres Password: " PG_PASS
echo

kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_DB=telegramdb \
  --from-literal=POSTGRES_USER="$PG_USER" \
  --from-literal=POSTGRES_PASSWORD="$PG_PASS" \
  -n database \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_USER="$PG_USER" \
  --from-literal=POSTGRES_PASSWORD="$PG_PASS" \
  -n telegram \
  --dry-run=client -o yaml | kubectl apply -f -

echo
echo "Creating Telegram Secret"

read -sp "Telegram Bot Token: " BOT_TOKEN
echo

kubectl create secret generic telegram-secret \
  --from-literal=BOT_TOKEN="$BOT_TOKEN" \
  -n telegram \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secrets Created Successfully"