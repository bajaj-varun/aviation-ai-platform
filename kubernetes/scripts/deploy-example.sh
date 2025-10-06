#!/bin/bash

# Set Kubernetes context
KUBE_CONTEXT="your-cluster-context"
NAMESPACE="aviation-platform"

echo "Starting Aviation Platform deployment..."

# Set Kubernetes context
kubectl config use-context $KUBE_CONTEXT

# Create namespace
echo "Creating namespace..."
kubectl apply -f kubernetes/namespace.yaml

# Create secrets (make sure to update these with your actual values)
echo "Creating secrets..."
kubectl create secret generic aviation-secrets \
  --namespace=$NAMESPACE \
  --from-literal=AWS_ACCESS_KEY_ID='your-aws-access-key' \
  --from-literal=AWS_SECRET_ACCESS_KEY='your-aws-secret-key' \
  --from-literal=SNOWFLAKE_USER='your-snowflake-user' \
  --from-literal=SNOWFLAKE_PASSWORD='your-snowflake-password' \
  --from-literal=SNOWFLAKE_ACCOUNT='your-account' \
  --from-literal=SNOWFLAKE_WAREHOUSE='AVIATION_WH' \
  --from-literal=SNOWFLAKE_DATABASE='AVIATION_DB' \
  --from-literal=SNOWFLAKE_SCHEMA='PUBLIC' \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy MongoDB
echo "Deploying MongoDB..."
kubectl apply -f kubernetes/mongodb-deployment.yaml

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to be ready..."
kubectl wait --for=condition=ready pod -l app=mongodb -n $NAMESPACE --timeout=300s

# Deploy backend
echo "Deploying backend..."
kubectl apply -f kubernetes/backend-deployment.yaml

# Deploy frontend
echo "Deploying frontend..."
kubectl apply -f kubernetes/frontend-deployment.yaml

# Deploy ingress
echo "Deploying ingress..."
kubectl apply -f kubernetes/ingress.yaml

# Wait for all pods to be ready
echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=300s

echo "Deployment completed successfully!"

# Display deployment status
echo "Current deployment status:"
kubectl get all -n $NAMESPACE

echo "Access the application at: http://aviation.local"