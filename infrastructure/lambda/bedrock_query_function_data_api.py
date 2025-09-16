import json
import os
import boto3
import time
from typing import Dict, Any

# Environment variables
SECRET_NAME = os.environ['SECRET_NAME']
REDSHIFT_HOST = os.environ['REDSHIFT_HOST']
REDSHIFT_DB = os.environ['REDSHIFT_DB']

bedrock_client = boto3.client('bedrock-runtime')
redshift_client = boto3.client('redshift-data')
secrets_client = boto3.client('secretsmanager')

def get_cluster_identifier():
    """Extract cluster identifier from host"""
    return REDSHIFT_HOST.split('.')[0]

def get_schema_info():
    """Get database schema information"""
    schema_info = """
    Database Schema:
    
    1. hr_data.departments
       - id (INTEGER, PRIMARY KEY): Department ID
       - department (VARCHAR(255)): Department name
    
    2. hr_data.jobs  
       - id (INTEGER, PRIMARY KEY): Job ID
       - job (VARCHAR(255)): Job title
    
    3. hr_data.hired_employees
       - id (INTEGER, PRIMARY KEY): Employee ID
       - name (VARCHAR(255)): Employee name
       - datetime (TIMESTAMPTZ): Hire date and time
       - department_id (INTEGER): References departments.id
       - job_id (INTEGER): References jobs.id
    """
    
    try:
        # Get data counts using Redshift Data API
        cluster_id = get_cluster_identifier()
        
        # Count departments
        dept_response = redshift_client.execute_statement(
            ClusterIdentifier=cluster_id,
            Database=REDSHIFT_DB,
            SecretArn=SECRET_NAME,
            Sql="SELECT COUNT(*) FROM hr_data.departments"
        )
        
        # Wait for completion and get result
        dept_count = wait_for_query_result(dept_response['Id'])
        
        schema_info += f"\nCurrent data counts:\n- Departments: {dept_count}\n- Jobs: Available\n- Employees: Available"
        
    except Exception as e:
        schema_info += f"\nNote: Could not retrieve current counts ({str(e)})"
    
    return schema_info

def wait_for_query_result(query_id, max_wait=30):
    """Wait for query to complete and return first result"""
    for _ in range(max_wait):
        response = redshift_client.describe_statement(Id=query_id)
        status = response['Status']
        
        if status == 'FINISHED':
            result = redshift_client.get_statement_result(Id=query_id)
            if result['Records']:
                return result['Records'][0][0]['longValue']
            return 0
        elif status == 'FAILED':
            raise Exception(f"Query failed: {response.get('Error', 'Unknown error')}")
        
        time.sleep(1)
    
    return "Unknown"

def execute_sql_query(sql_query: str):
    """Execute SQL query using Redshift Data API"""
    try:
        cluster_id = get_cluster_identifier()
        
        response = redshift_client.execute_statement(
            ClusterIdentifier=cluster_id,
            Database=REDSHIFT_DB,
            SecretArn=SECRET_NAME,
            Sql=sql_query
        )
        
        query_id = response['Id']
        
        # Wait for completion
        for _ in range(30):
            status_response = redshift_client.describe_statement(Id=query_id)
            status = status_response['Status']
            
            if status == 'FINISHED':
                result = redshift_client.get_statement_result(Id=query_id)
                
                # Extract column names
                columns = [col['name'] for col in result['ColumnMetadata']]
                
                # Extract rows
                rows = []
                for record in result['Records']:
                    row = []
                    for field in record:
                        if 'stringValue' in field:
                            row.append(field['stringValue'])
                        elif 'longValue' in field:
                            row.append(field['longValue'])
                        elif 'isNull' in field:
                            row.append(None)
                        else:
                            row.append(str(field))
                    rows.append(row)
                
                return {
                    "columns": columns,
                    "rows": rows,
                    "count": len(rows)
                }
            elif status == 'FAILED':
                return {"error": status_response.get('Error', 'Query failed')}
            
            time.sleep(1)
        
        return {"error": "Query timeout"}
        
    except Exception as e:
        return {"error": str(e)}

def query_bedrock(question: str, schema_info: str):
    """Query Bedrock model with context"""
    
    prompt = f"""You are a helpful assistant that answers questions about HR data in a Redshift database.

{schema_info}

Rules:
1. Only answer questions related to the HR data (departments, jobs, employees)
2. If asked to generate SQL, use proper Redshift syntax
3. For non-HR questions, politely decline and redirect to HR topics
4. Be concise and accurate

Question: {question}

Answer:"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = bedrock_client.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(body)
    )
    
    result = json.loads(response['body'].read())
    return result['content'][0]['text']

def lambda_handler(event, context):
    try:
        method = event['httpMethod']
        path = event['path']
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        if method == 'POST' and path == '/ask':
            question = body.get('question')
            if not question:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Question is required'})
                }
            
            # Get schema information
            schema_info = get_schema_info()
            
            # Query Bedrock
            answer = query_bedrock(question, schema_info)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'question': question,
                    'answer': answer
                })
            }
        
        elif method == 'POST' and path == '/sql':
            sql_query = body.get('sql')
            if not sql_query:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'SQL query is required'})
                }
            
            # Execute SQL query
            result = execute_sql_query(sql_query)
            
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Not found'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
