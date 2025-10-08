#!/bin/bash

NAMESPACE="aviation-platform" 
# SELECTOR="app=backend" 
SELECTOR="app=frontend" 


k get pods,svc,secrets,ing -n $NAMESPACE


k logs -n "$NAMESPACE" -l "$SELECTOR" --all-containers=true
