#!/bin/bash

# Set variables 
# TODO: need to read from env file, currently hardcoded
REGISTRY=your-registry.io
NAMESPACE=aviation
VERSION=1.0.0

# Build backend image
echo "Building backend image..."
docker build -t $REGISTRY/$NAMESPACE/backend:$VERSION ./backend
docker push $REGISTRY/$NAMESPACE/backend:$VERSION

# Build frontend image
echo "Building frontend image..."
docker build -t $REGISTRY/$NAMESPACE/frontend:$VERSION ./frontend
docker push $REGISTRY/$NAMESPACE/frontend:$VERSION

echo "Images built and pushed successfully!"