import requests
import json

# Your API Gateway URL
API_URL = "https://euvoczmkf2.execute-api.us-east-1.amazonaws.com/Prod"

def test_insert_departments():
    url = f"{API_URL}/data/departments"
    data = {
        "data": [
            {"id": 1, "department": "Engineering"},
            {"id": 2, "department": "Sales"}
        ]
    }
    response = requests.post(url, json=data)
    print(f"Insert departments: {response.status_code} - {response.text}")

def test_insert_jobs():
    url = f"{API_URL}/data/jobs"
    data = {
        "data": [
            {"id": 1, "job": "Software Engineer"},
            {"id": 2, "job": "Sales Manager"}
        ]
    }
    response = requests.post(url, json=data)
    print(f"Insert jobs: {response.status_code} - {response.text}")

def test_insert_employees():
    url = f"{API_URL}/data/hired_employees"
    data = {
        "data": [
            {"id": 1, "name": "John Doe", "datetime": "2023-01-15T10:00:00", "department_id": 1, "job_id": 1}
        ]
    }
    response = requests.post(url, json=data)
    print(f"Insert employees: {response.status_code} - {response.text}")

def test_backup():
    url = f"{API_URL}/backup/departments"
    response = requests.post(url)
    print(f"Backup: {response.status_code} - {response.text}")
    return response.json().get('backup_key') if response.status_code == 200 else None

def test_restore(backup_key):
    url = f"{API_URL}/restore/departments"
    data = {"backup_key": backup_key}
    response = requests.post(url, json=data)
    print(f"Restore: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Testing Redshift Data API...")
    test_insert_departments()
    test_insert_jobs()
    test_insert_employees()
    backup_key = test_backup()
    if backup_key:
        test_restore(backup_key)
