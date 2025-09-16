#!/usr/bin/env python3
"""
Test script for HR Data API report endpoints
"""

import requests
import json

# API Configuration
BASE_URL = "https://euvoczmkf2.execute-api.us-east-1.amazonaws.com/Prod"

def test_quarterly_hiring_report():
    """Test quarterly hiring report endpoint"""
    print("Testing Quarterly Hiring Report...")
    
    # Test with default year (2021)
    response = requests.get(f"{BASE_URL}/reports/quarterly_hiring_report")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Columns: {data['columns']}")
        print(f"Row count: {data['count']}")
        if data['rows']:
            print("Sample data:")
            for i, row in enumerate(data['rows'][:3]):  # Show first 3 rows
                print(f"  Row {i+1}: {row}")
        else:
            print("No data returned")
    else:
        print(f"Error: {response.text}")
    
    # Test with specific year
    print("\nTesting with year parameter (2022)...")
    response = requests.get(f"{BASE_URL}/reports/quarterly_hiring_report?year=2022")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Row count for 2022: {data['count']}")
    else:
        print(f"Error: {response.text}")

def test_departments_above_avg_hiring():
    """Test departments above average hiring endpoint"""
    print("\n" + "="*50)
    print("Testing Departments Above Average Hiring Report...")
    
    # Test with default year (2021)
    response = requests.get(f"{BASE_URL}/reports/departments_above_avg_hiring")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Columns: {data['columns']}")
        print(f"Row count: {data['count']}")
        if data['rows']:
            print("Sample data:")
            for i, row in enumerate(data['rows'][:3]):  # Show first 3 rows
                print(f"  Row {i+1}: {row}")
        else:
            print("No departments above average")
    else:
        print(f"Error: {response.text}")
    
    # Test with specific year
    print("\nTesting with year parameter (2023)...")
    response = requests.get(f"{BASE_URL}/reports/departments_above_avg_hiring?year=2023")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Row count for 2023: {data['count']}")
    else:
        print(f"Error: {response.text}")

def test_invalid_endpoints():
    """Test error handling"""
    print("\n" + "="*50)
    print("Testing Error Handling...")
    
    # Test invalid report type
    response = requests.get(f"{BASE_URL}/reports/invalid_report")
    print(f"Invalid report type - Status Code: {response.status_code}")
    
    # Test invalid year
    response = requests.get(f"{BASE_URL}/reports/quarterly_hiring_report?year=1999")
    print(f"Invalid year - Status Code: {response.status_code}")
    
    # Test non-numeric year
    response = requests.get(f"{BASE_URL}/reports/quarterly_hiring_report?year=abc")
    print(f"Non-numeric year - Status Code: {response.status_code}")

if __name__ == "__main__":
    print("HR Data API - Reports Endpoint Tests")
    print("="*50)
    
    try:
        test_quarterly_hiring_report()
        test_departments_above_avg_hiring()
        test_invalid_endpoints()
        
        print("\n" + "="*50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
