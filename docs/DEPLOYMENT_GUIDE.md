# Deployment Guide

Complete step-by-step deployment guide for the Redshift Data API Reference Architecture.

## Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed and running
- Python 3.12+ for local testing
- Redshift cluster with public access enabled

## Step 1: Database Setup

### 1.1 Create Redshift Tables
```bash
# Connect to your Redshift cluster and create tables with primary keys
psql -h your-cluster.redshift.amazonaws.com -U awsuser -d demo_db -f database/ddl/create_tables_with_pk.sql
```

### 1.2 Verify Tables Created
```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables WHERE table_schema = 'hr_data';

-- Verify primary keys
SELECT * FROM hr_data.departments LIMIT 5;
SELECT * FROM hr_data.jobs LIMIT 5;
SELECT * FROM hr_data.hired_employees LIMIT 5;
```

## Step 2: Configure Deployment Scripts

### 2.1 Update Data API Configuration
Edit `scripts/deploy.sh`:
```bash
S3_BUCKET="your-unique-bucket-name"
SECRET_NAME="arn:aws:secretsmanager:us-east-1:account:secret:name"
REDSHIFT_HOST="your-cluster.region.redshift.amazonaws.com"
```

### 2.2 Update Bedrock API Configuration
Edit `scripts/deploy_bedrock.sh`:
```bash
S3_BUCKET="your-unique-bucket-name"
SECRET_NAME="arn:aws:secretsmanager:us-east-1:account:secret:name"
REDSHIFT_HOST="your-cluster.region.redshift.amazonaws.com"
```

## Step 3: Deploy Lambda APIs

### 3.1 Deploy Data Management API
```bash
# Deploy CRUD operations API
./scripts/deploy.sh
```

**Expected Output:**
```
Successfully created/updated stack - redshift-data-api in us-east-1
```

**Get API URL:**
```bash
aws cloudformation describe-stacks --stack-name redshift-data-api --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' --output text
```

### 3.2 Deploy Bedrock AI Query API
```bash
# Deploy AI-powered query API
./scripts/deploy_bedrock.sh
```

**Expected Output:**
```
Successfully created/updated stack - bedrock-query-api in us-east-1
```

**Get Bedrock API URL:**
```bash
aws cloudformation describe-stacks --stack-name bedrock-query-api --query 'Stacks[0].Outputs[?OutputKey==`BedrockApiUrl`].OutputValue' --output text
```

### 3.3 Test Lambda APIs
```bash
# Test Bedrock API
python tests/test_bedrock_api.py

# Test Data API with Postman
# Import tests/Redshift_Data_API.postman_collection.json
```

## Step 4: Deploy Streamlit Web Application

### 4.1 Update ECS Configuration
Edit `scripts/deploy_ecs.sh` with your Bedrock API URL:
```bash
BEDROCK_API_URL="https://your-bedrock-api-id.execute-api.us-east-1.amazonaws.com/Prod"
```

### 4.2 Deploy to ECS Fargate
```bash
# Deploy containerized Streamlit app with Cognito
./scripts/deploy_ecs.sh
```

**This will:**
1. Create ECR repository
2. Build and push Docker image
3. Create Cognito User Pool
4. Deploy ECS Fargate service
5. Create Application Load Balancer
6. Set up VPC and networking

**Expected Output:**
```
Deployment complete!
App URL: http://hr-streamlit-alb-xxxxxxxxx.us-east-1.elb.amazonaws.com
```

### 4.3 Create Test Users (Optional)
```bash
# Create a test user for login
./scripts/create_test_user.sh
```

## Step 5: Verification

### 5.1 Test Data API
```bash
# Test with curl
curl -X POST https://your-data-api-url/data/departments \
  -H "Content-Type: application/json" \
  -d '{"data": [{"id": 1, "department": "Engineering"}]}'
```

### 5.2 Test Bedrock API
```bash
# Test AI queries
curl -X POST https://your-bedrock-api-url/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many employees do we have?"}'
```

### 5.3 Test Streamlit App
1. Open the Load Balancer URL in browser
2. Register a new user or use test credentials
3. Test all features:
   - Query Data (view tables, run SQL)
   - Insert Data (add departments, jobs, employees)
   - Ask AI (natural language queries)

## Step 6: Post-Deployment Configuration

### 6.1 Create Cognito Users
```bash
# Via AWS Console: Cognito > User Pools > hr-data-users > Users
# Or via CLI:
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username newuser \
  --user-attributes Name=email,Value=user@example.com \
  --message-action SUPPRESS
```

### 6.2 Set User Passwords
```bash
aws cognito-idp admin-set-user-password \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username newuser \
  --password "SecurePass123!" \
  --permanent
```

## Deployment Outputs Summary

After successful deployment, you'll have:

| Component | URL/ID | Purpose |
|-----------|--------|---------|
| Data API | `https://xxx.execute-api.us-east-1.amazonaws.com/Prod` | CRUD operations |
| Bedrock API | `https://yyy.execute-api.us-east-1.amazonaws.com/Prod` | AI queries |
| Streamlit App | `http://alb-xxx.us-east-1.elb.amazonaws.com` | Web interface |
| Cognito Pool | `us-east-1_xxxxxxxxx` | User authentication |
| Cognito Client | `xxxxxxxxxxxxxxxxx` | App integration |

## Troubleshooting

### Lambda Deployment Issues
```bash
# Check SAM build logs
sam logs -n YourFunctionName --stack-name your-stack-name

# Check CloudWatch logs
./scripts/check_bedrock_logs.sh
```

### ECS Deployment Issues
```bash
# Check ECS service status
aws ecs describe-services --cluster hr-streamlit-cluster --services hr-streamlit-service

# Check container logs
aws logs get-log-events --log-group-name /ecs/hr-streamlit --log-stream-name ecs/streamlit-app/xxx
```

### Cognito Issues
```bash
# List user pools
aws cognito-idp list-user-pools --max-results 10

# Check user pool details
aws cognito-idp describe-user-pool --user-pool-id us-east-1_xxxxxxxxx
```

## Cleanup

To remove all resources:
```bash
# Delete CloudFormation stacks
aws cloudformation delete-stack --stack-name hr-streamlit-ecs
aws cloudformation delete-stack --stack-name bedrock-query-api
aws cloudformation delete-stack --stack-name redshift-data-api

# Delete ECR repository
aws ecr delete-repository --repository-name hr-streamlit-app --force
```

## Next Steps

1. **Security**: Configure HTTPS with ACM certificate
2. **Monitoring**: Set up CloudWatch dashboards and alarms
3. **Scaling**: Configure ECS auto-scaling policies
4. **Backup**: Set up automated S3 backup schedules
5. **CI/CD**: Implement automated deployment pipelines
