#!/bin/bash

echo "========== Namespaces =========="
kubectl get ns

echo
echo "========== Pods =========="
kubectl get pods -A

echo
echo "========== Deployments =========="
kubectl get deployments -A

echo
echo "========== Services =========="
kubectl get svc -A

echo
echo "========== PVC =========="
kubectl get pvc -A

echo
echo "========== PV =========="
kubectl get pv