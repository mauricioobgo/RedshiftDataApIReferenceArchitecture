import boto3
import json
import pytest

# Configuration
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
AWS_REGION = "us-east-1"

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)

def test_bedrock_basic_inference():
    """Test basic Bedrock model inference"""
    
    prompt = "What is Amazon Redshift?"
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = bedrock_client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body)
    )
    
    result = json.loads(response['body'].read())
    answer = result['content'][0]['text']
    
    assert len(answer) > 0
    assert "redshift" in answer.lower()
    print(f"✅ Basic inference test passed")
    print(f"Answer: {answer[:100]}...")

def test_bedrock_hr_context():
    """Test Bedrock with HR database context"""
    
    schema_context = """
    Database Schema:
    1. hr_data.departments - id (PK), department
    2. hr_data.jobs - id (PK), job  
    3. hr_data.hired_employees - id (PK), name, datetime, department_id, job_id
    """
    
    prompt = f"""You are an HR data assistant. {schema_context}
    
    Question: How would I find all employees in the Engineering department?
    
    Answer:"""
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = bedrock_client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body)
    )
    
    result = json.loads(response['body'].read())
    answer = result['content'][0]['text']
    
    assert len(answer) > 0
    assert any(keyword in answer.upper() for keyword in ["SELECT", "JOIN", "WHERE"])
    print(f"✅ HR context test passed")
    print(f"SQL suggestion: {answer}")

def test_bedrock_sql_generation():
    """Test Bedrock SQL generation for HR data"""
    
    prompt = """Generate a SQL query to count employees by department using these tables:
    - hr_data.departments (id, department)
    - hr_data.hired_employees (id, name, department_id, job_id)
    
    SQL:"""
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 150,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = bedrock_client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body)
    )
    
    result = json.loads(response['body'].read())
    answer = result['content'][0]['text']
    
    assert "SELECT" in answer.upper()
    assert "COUNT" in answer.upper()
    assert "GROUP BY" in answer.upper()
    assert "hr_data" in answer
    print(f"✅ SQL generation test passed")
    print(f"Generated SQL: {answer}")

def test_bedrock_non_hr_rejection():
    """Test that Bedrock rejects non-HR questions"""
    
    prompt = """You only answer HR data questions. 
    
    Question: What's the weather like today?
    
    Answer:"""
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = bedrock_client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body)
    )
    
    result = json.loads(response['body'].read())
    answer = result['content'][0]['text']
    
    # Should politely decline or redirect to HR topics
    assert any(keyword in answer.lower() for keyword in ["sorry", "can't", "hr", "data", "help"])
    print(f"✅ Non-HR rejection test passed")
    print(f"Response: {answer}")

if __name__ == "__main__":
    print("Testing Bedrock Inference for HR Data Assistant...")
    print("=" * 50)
    
    try:
        test_bedrock_basic_inference()
        print()
        test_bedrock_hr_context()
        print()
        test_bedrock_sql_generation()
        print()
        test_bedrock_non_hr_rejection()
        print()
        print("🎉 All Bedrock inference tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
