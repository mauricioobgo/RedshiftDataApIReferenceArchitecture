# Redshift Data API Reference Architecture

A complete serverless HR data management system with REST APIs, AI-powered queries, and web interface.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Lambda APIs    │    │   Amazon        │
│   Web App       │───▶│   - Data CRUD    │───▶│   Redshift      │
│   (ECS Fargate) │    │   - AI Queries   │    │   Cluster       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Amazon        │    │   Amazon         │    │   Amazon S3     │
│   Cognito       │    │   Bedrock        │    │   (AVRO         │
│   (Auth)        │    │   (Claude 3)     │    │   Backups)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Features

- **REST API**: CRUD operations with batch insert (1-1000 rows)
- **AI Queries**: Natural language queries using Amazon Bedrock (Claude 3 Haiku)
- **Web Interface**: Streamlit app with Cognito authentication
- **Data Backup**: AVRO format backups to S3
- **Serverless**: Lambda functions and ECS Fargate
- **Security**: Cognito user pools, IAM roles, primary key constraints

## Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Docker installed
- Python 3.12+ for local testing

### 1. Deploy Database
```bash
# Create Redshift tables with primary keys
psql -h your-cluster.redshift.amazonaws.com -U awsuser -d demo_db -f database/ddl/create_tables_with_pk.sql
```

### 2. Deploy Lambda APIs

**Update configuration first:**
Edit `scripts/deploy.sh` and `scripts/deploy_bedrock.sh` with your values:
- S3_BUCKET
- SECRET_NAME (Secrets Manager ARN)
- REDSHIFT_HOST

```bash
# Deploy Data Management API
./scripts/deploy.sh

# Deploy Bedrock AI Query API
./scripts/deploy_bedrock.sh
```

### 3. Deploy Web Application

**Update configuration:**
Edit `scripts/deploy_ecs.sh` with your Bedrock API URL from step 2.

```bash
# Deploy Streamlit app with Cognito to ECS
./scripts/deploy_ecs.sh
```

This creates:
- Cognito User Pool for authentication
- Docker container with Streamlit app
- ECS Fargate service
- Application Load Balancer
- Complete VPC infrastructure

## Project Structure

```
├── README.md
├── requirements.txt
├── .gitignore
├── database/
│   ├── ddl/                    # Database schema definitions
│   │   ├── setup.sql
│   │   ├── transformations.sql
│   │   └── create_tables_with_pk.sql
│   └── migrations/             # Database migrations
├── infrastructure/
│   ├── lambda/                 # Lambda function deployments
│   │   ├── lambda_function.py
│   │   ├── bedrock_query_function_data_api.py
│   │   ├── template.yaml
│   │   ├── bedrock_template.yaml
│   │   └── requirements.txt
│   ├── ecs/                    # ECS Fargate deployment
│   │   └── ecs_template.yaml
│   └── cognito/                # Standalone Cognito setup (optional)
│       └── cognito_setup.yaml
├── frontend/
│   ├── streamlit/              # Streamlit web application
│   │   └── streamlit_app.py
│   ├── docker/                 # Docker configuration
│   │   └── Dockerfile
│   └── requirements_streamlit.txt
├── scripts/                    # Deployment and utility scripts
│   ├── deploy.sh
│   ├── deploy_bedrock.sh
│   ├── deploy_ecs.sh
│   ├── create_test_user.sh
│   └── check_bedrock_logs.sh
├── tests/                      # API tests and collections
│   ├── test_bedrock_inference.py
│   ├── test_bedrock_api.py
│   ├── test_simple_bedrock.py
│   ├── Redshift_Data_API.postman_collection.json
│   └── Bedrock_Query_API.postman_collection.json
└── docs/                       # Documentation
```

## API Endpoints

### Data Management API
- `POST /data/{table}` - Insert batch data (1-1000 rows, prevents duplicates)
- `POST /backup/{table}` - Backup table to S3 (AVRO format)
- `POST /restore/{table}` - Restore table from backup

### AI Query API
- `POST /ask` - Ask natural language questions about HR data
- `POST /sql` - Execute SQL queries directly using Redshift Data API

## Data Models

### Tables (with Primary Keys)
- **departments**: `id` (PK), `department`
- **jobs**: `id` (PK), `job`
- **hired_employees**: `id` (PK), `name`, `datetime`, `department_id`, `job_id`

### Validation Rules
- All tables: ID field required, primary key constraints prevent duplicates
- Departments/Jobs: Name required, max 255 chars
- Employees: Datetime auto-generated on insert, optional department_id/job_id

## Configuration

### Required Environment Variables

**Lambda Functions:**
```bash
SECRET_NAME=arn:aws:secretsmanager:region:account:secret:name
REDSHIFT_HOST=cluster.region.redshift.amazonaws.com
REDSHIFT_DB=database_name
S3_BUCKET=backup-bucket-name
```

**Streamlit App (auto-configured in ECS):**
```bash
DATA_API_URL=https://api-id.execute-api.region.amazonaws.com/Prod
BEDROCK_API_URL=https://bedrock-api-id.execute-api.region.amazonaws.com/Prod
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=us-east-1
```

## Testing

### API Testing
```bash
# Test Bedrock inference directly
python tests/test_bedrock_inference.py

# Test Bedrock API endpoints
python tests/test_bedrock_api.py

# Simple connectivity test
python tests/test_simple_bedrock.py

# Postman collections available in tests/
```

### Create Test Users
```bash
# Create a test user in Cognito (after ECS deployment)
./scripts/create_test_user.sh
```

## Deployment Outputs

After successful deployment, you'll get:

1. **Data API URL**: For CRUD operations
2. **Bedrock API URL**: For AI queries  
3. **Streamlit App URL**: Public web interface via Load Balancer
4. **Cognito User Pool ID**: For user management
5. **Cognito Client ID**: For app authentication

## Security Features

- **Authentication**: AWS Cognito User Pools with configurable password policies
- **Authorization**: IAM roles with least privilege principles
- **Data Protection**: Secrets Manager for database credentials
- **Network Security**: VPC with public/private subnets and security groups
- **Database Security**: Primary key constraints, duplicate prevention
- **API Security**: CORS enabled, input validation

## Monitoring & Logging

- **CloudWatch Logs**: All Lambda functions and ECS tasks
- **CloudWatch Metrics**: API Gateway, Lambda, ECS, and Load Balancer metrics
- **Health Checks**: Load balancer health checks for Streamlit app
- **Log Retention**: 7 days for ECS logs

## Cost Optimization

- **Serverless**: Pay-per-use Lambda functions
- **Fargate**: Right-sized container resources (256 CPU, 512 MB memory)
- **S3 Lifecycle**: Automatic backup archival policies
- **Redshift**: Pause/resume cluster when not in use
- **Single AZ**: Development-optimized networking

## Troubleshooting

### Common Issues

**Lambda 502 Errors:**
```bash
# Check CloudWatch logs
./scripts/check_bedrock_logs.sh
```

**Bedrock Access Issues:**
- Ensure Bedrock model access is enabled in AWS Console
- Check IAM permissions for bedrock:InvokeModel

**Streamlit Authentication Issues:**
- Verify Cognito User Pool and Client IDs in environment variables
- Create test users via AWS Console or CLI

**Database Connection Issues:**
- Verify Secrets Manager contains correct credentials
- Check Redshift cluster is publicly accessible (if using public endpoint)
- Ensure security groups allow Lambda access

## Architecture Decisions

- **Redshift Data API**: Eliminates need for psycopg2 in Lambda, more serverless-friendly
- **Claude 3 Haiku**: Cost-effective model for HR query assistance
- **ECS Fargate**: Serverless containers, no EC2 management
- **Application Load Balancer**: HTTP/HTTPS termination and health checks
- **Primary Keys**: Database-level duplicate prevention

## Contributing

1. Follow the established folder structure
2. Update tests for new features
3. Document configuration changes in README
4. Use Infrastructure as Code (CloudFormation/SAM)
5. Test locally before deployment

## License

This project is licensed under the MIT License.
