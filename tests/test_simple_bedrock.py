import requests
import json

# Test with minimal payload
BEDROCK_API_URL = "https://k86bczfnj3.execute-api.us-east-1.amazonaws.com/Prod"

def test_simple_ask():
    """Test with simple question"""
    url = f"{BEDROCK_API_URL}/ask"
    data = {"question": "Hello"}
    
    print(f"Testing: {url}")
    print(f"Payload: {data}")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            return result
        else:
            print("❌ Failed")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

if __name__ == "__main__":
    test_simple_ask()
