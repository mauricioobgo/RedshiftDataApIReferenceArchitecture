#!/bin/bash

# Deploy Cognito User Pool separately

STACK_NAME="hr-cognito-pool"
REGION="us-east-1"

echo "Deploying Cognito User Pool..."

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../"

# Deploy Cognito stack
aws cloudformation deploy \
  --template-file infrastructure/cognito/cognito_setup.yaml \
  --stack-name $STACK_NAME \
  --region $REGION

# Get outputs
USER_POOL_ID=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' --output text)
CLIENT_ID=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ClientId`].OutputValue' --output text)

echo ""
echo "Cognito deployment complete!"
echo "User Pool ID: $USER_POOL_ID"
echo "Client ID: $CLIENT_ID"
echo ""
echo "Use these values for ECS deployment"
