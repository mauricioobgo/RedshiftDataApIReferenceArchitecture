#!/bin/bash

# Build and push Docker image only

REGION="us-east-1"
ECR_REPO="hr-streamlit-app"

echo "Building and pushing Docker image..."

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../"

# Create ECR repository
#aws ecr create-repository --repository-name $ECR_REPO --region $REGION || true

# Get ECR login
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com

# Build and push Docker image
IMAGE_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest

docker build -f frontend/docker/Dockerfile -t $ECR_REPO .
docker tag $ECR_REPO:latest $IMAGE_URI
docker push $IMAGE_URI

echo "Image pushed to: $IMAGE_URI"
