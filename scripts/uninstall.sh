#!/bin/bash

echo "Removing Telegram Bot..."
kubectl delete -f k8s/telegram/

echo "Removing PostgreSQL..."
kubectl delete -f k8s/postgres/

echo "Removing Namespaces..."
kubectl delete -f k8s/namespaces.yaml

echo "Cleanup Complete"