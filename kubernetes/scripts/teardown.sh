#!/bin/bash

NAMESPACE="aviation-platform"

echo "Tearing down Aviation Platform..."

kubectl delete -f kubernetes/ingress.yaml
kubectl delete -f kubernetes/frontend-deployment.yaml
kubectl delete -f kubernetes/backend-deployment.yaml
kubectl delete -f kubernetes/mongodb-deployment.yaml
kubectl delete secret aviation-secrets -n $NAMESPACE
kubectl delete configmap aviation-config -n $NAMESPACE
kubectl delete configmap frontend-config -n $NAMESPACE
kubectl delete namespace $NAMESPACE

echo "Teardown completed!"