import json
import os
import boto3
import psycopg2
from typing import Dict, Any

# Environment variables
SECRET_NAME = os.environ['SECRET_NAME']
REDSHIFT_HOST = os.environ['REDSHIFT_HOST']
REDSHIFT_DB = os.environ['REDSHIFT_DB']

bedrock_client = boto3.client('bedrock-runtime')
secrets_client = boto3.client('secretsmanager')

def get_db_connection():
    secret = secrets_client.get_secret_value(SecretId=SECRET_NAME)
    creds = json.loads(secret['SecretString'])
    
    return psycopg2.connect(
        host=REDSHIFT_HOST,
        database=REDSHIFT_DB,
        user=creds['username'],
        password=creds['password'],
        port=5439
    )

def get_schema_info():
    """Get database schema information"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
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
        
        # Get sample data counts
        cur.execute("SELECT COUNT(*) FROM hr_data.departments")
        dept_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM hr_data.jobs")
        job_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM hr_data.hired_employees")
        emp_count = cur.fetchone()[0]
        
        schema_info += f"\nCurrent data counts:\n- Departments: {dept_count}\n- Jobs: {job_count}\n- Employees: {emp_count}"
        
        return schema_info
    finally:
        cur.close()
        conn.close()

def execute_sql_query(sql_query: str):
    """Execute SQL query and return results"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        
        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "count": len(rows)
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

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
