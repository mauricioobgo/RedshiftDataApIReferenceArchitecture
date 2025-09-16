#!/bin/bash

# Deploy script for Bedrock Query API

STACK_NAME="bedrock-query-api"
S3_BUCKET="aws-redshift-demo-jkashdjkahskdjhsdkj"
SECRET_NAME="arn:aws:secretsmanager:us-east-1:211125742711:secret:redshift!redshift-cluster-demo-awsuser-KEJnZ9"
REDSHIFT_HOST="redshift-cluster-demo.chgw5selsumb.us-east-1.redshift.amazonaws.com"

echo "Building and deploying Bedrock Query Lambda function..."

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../infrastructure/lambda"

sam build -t bedrock_template.yaml
sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name $STACK_NAME \
  --region "us-east-1" \
  --s3-bucket $S3_BUCKET \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    SecretName=$SECRET_NAME \
    RedshiftHost=$REDSHIFT_HOST \
    RedshiftDB="demo_db"

echo "Deployment complete!"
