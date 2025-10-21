#!/bin/bash

NS="aviation-platform" 
# SELECTOR="app=backend" 
SELECTOR="app=frontend" 

eksctl get --cluster aviation-ai-cluster nodegroup --region ap-south-1 --profile aviation-infra

k get pods,svc,secrets,ing -n $NS


k logs -n "$NS" -l "$SELECTOR" --all-containers=true


helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=aviation-ai-cluster \
  --set serviceAccount.create=true \
  --set serviceAccount.name=aws-load-balancer-controller

# Get the AWS Load Balancer Controller pods
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller

# Check controller logs
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller --tail=50

# If you have multiple pods, specify one
kubectl logs -n kube-system deployment/aws-load-balancer-controller --tail=50


error -
{
    "level": "error",
    "ts": "2025-10-10T14:02:57Z",
    "msg": "Reconciler error",
    "controller": "ingress",
    "object": {
        "name": "aviation-alb-ingress",
        "namespace": "aviation-platform"
    },
    "namespace": "aviation-platform",
    "name": "aviation-alb-ingress",
    "reconcileID": "70fb85d5-a96c-45c5-b884-3303880ab4ed",
    "error": "operation error Elastic Load Balancing v2: DescribeLoadBalancers, https response error StatusCode: 403, RequestID: 410da1b6-23a6-48d1-8d29-19c46a277ff6, api error AccessDenied: User: <<>> is not authorized to perform: elasticloadbalancing:DescribeLoadBalancers because no identity-based policy allows the elasticloadbalancing:DescribeLoadBalancers action"
}

Debug the error -
# Check if the AWS Load Balancer Controller is running
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller

# Check the service account
kubectl get serviceaccount -n kube-system aws-load-balancer-controller

# Describe the pod to see IAM role
kubectl describe pod -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller


Fix IAM error -
# Get your cluster name
eksctl get cluster

# Create OIDC provider (replace with your cluster name)
eksctl utils associate-iam-oidc-provider \
    --region ap-south-1 \
    --cluster aviation-ai-cluster \
    --approve --profile aviation-infra

# Create the IAM service account with proper permissions:
# Create the IAM service account for ALB Controller
eksctl create iamserviceaccount \
    --region ap-south-1 \
    --name aws-load-balancer-controller \
    --namespace kube-system \
    --cluster aviation-ai-cluster \
    --attach-policy-arn arn:aws:iam::aws:policy/AWSLoadBalancerControllerIAMPolicy \
    --override-existing-serviceaccounts \
    --approve --profile aviation-infra
