#!/bin/bash

# Setup and run Streamlit app

echo "Setting up Streamlit HR Data App..."

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../"

# Install requirements
pip install -r frontend/requirements_streamlit.txt

# Deploy Cognito (if not already deployed)
echo "Deploying Cognito User Pool..."
aws cloudformation deploy \
  --template-file infrastructure/cognito/cognito_setup.yaml \
  --stack-name hr-cognito-pool \
  --region us-east-1

# Get Cognito details
USER_POOL_ID=$(aws cloudformation describe-stacks --stack-name hr-cognito-pool --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' --output text)
CLIENT_ID=$(aws cloudformation describe-stacks --stack-name hr-cognito-pool --query 'Stacks[0].Outputs[?OutputKey==`ClientId`].OutputValue' --output text)

echo "User Pool ID: $USER_POOL_ID"
echo "Client ID: $CLIENT_ID"
echo ""
echo "Update frontend/streamlit/streamlit_app.py with these values, then run:"
echo "streamlit run frontend/streamlit/streamlit_app.py"
