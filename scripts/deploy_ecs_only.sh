#!/bin/bash

# Deploy ECS stack using latest image and existing Cognito

STACK_NAME="hr-streamlit-ecs"
COGNITO_STACK_NAME="hr-cognito-pool"
REGION="us-east-1"
ECR_REPO="hr-streamlit-app"

echo "Deploying ECS stack with latest image..."

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../"

# Use latest image from ECR
IMAGE_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest

# Get Cognito details from existing stack
USER_POOL_ID="us-east-1_For7auvNQ"
CLIENT_ID="4ooo0mvaf3b71v0o4elmbonf3c"
echo "Using image: $IMAGE_URI"
echo "Using Cognito Pool: $USER_POOL_ID"
echo "Using Cognito Client: $CLIENT_ID"

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file infrastructure/ecs/ecs_template.yaml \
  --stack-name $STACK_NAME \
  --region $REGION \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    ImageUri=$IMAGE_URI \
    CognitoUserPoolId=$USER_POOL_ID \
    CognitoClientId=$CLIENT_ID

# Get outputs
LOAD_BALANCER_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' --output text)

echo ""
echo "ECS deployment complete!"
echo "App URL: $LOAD_BALANCER_URL"
echo ""
