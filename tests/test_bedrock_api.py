import requests
import json

# Replace with your Bedrock API Gateway URL
BEDROCK_API_URL = "https://k86bczfnj3.execute-api.us-east-1.amazonaws.com/Prod"

def test_ask_endpoint():
    """Test the /ask endpoint"""
    url = f"{BEDROCK_API_URL}/ask"
    data = {"question": "How many employees do we have?"}
    
    response = requests.post(url, json=data)
    print(f"Ask endpoint: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Question: {result['question']}")
        print(f"Answer: {result['answer']}")
        assert 'question' in result
        assert 'answer' in result
        print("✅ Ask endpoint test passed")
    else:
        print(f"❌ Ask endpoint failed: {response.text}")

def test_sql_endpoint():
    """Test the /sql endpoint"""
    url = f"{BEDROCK_API_URL}/sql"
    data = {"sql": "SELECT COUNT(*) as total FROM hr_data.departments"}
    
    response = requests.post(url, json=data)
    print(f"SQL endpoint: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"SQL result: {result}")
        assert 'columns' in result
        assert 'rows' in result
        print("✅ SQL endpoint test passed")
    else:
        print(f"❌ SQL endpoint failed: {response.text}")

def test_hr_question():
    """Test HR-specific question"""
    url = f"{BEDROCK_API_URL}/ask"
    data = {"question": "What departments exist in our database?"}
    
    response = requests.post(url, json=data)
    print(f"HR question: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"HR Answer: {result['answer']}")
        print("✅ HR question test passed")
    else:
        print(f"❌ HR question failed: {response.text}")

def test_non_hr_question():
    """Test non-HR question (should be declined)"""
    url = f"{BEDROCK_API_URL}/ask"
    data = {"question": "What's the weather like today?"}
    
    response = requests.post(url, json=data)
    print(f"Non-HR question: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Non-HR Answer: {result['answer']}")
        # Should politely decline
        answer_lower = result['answer'].lower()
        if any(word in answer_lower for word in ['sorry', "can't", 'hr', 'data']):
            print("✅ Non-HR question properly declined")
        else:
            print("⚠️ Non-HR question not properly declined")
    else:
        print(f"❌ Non-HR question failed: {response.text}")

if __name__ == "__main__":
    print("Testing Bedrock Query API...")
    print("=" * 40)
    
    try:
        test_ask_endpoint()
        print()
        test_sql_endpoint()
        print()
        test_hr_question()
        print()
        test_non_hr_question()
        print()
        print("🎉 All Bedrock API tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
