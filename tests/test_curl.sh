#!/bin/bash

# Your API Gateway URL
API_URL="https://euvoczmkf2.execute-api.us-east-1.amazonaws.com/Prod"

echo "Testing Redshift Data API with curl..."

# Test insert departments
echo "1. Insert departments:"
curl -X POST "$API_URL/data/departments" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"id": 1, "department": "Engineering"},
      {"id": 2, "department": "Sales"}
    ]
  }'
echo -e "\n"

# Test insert jobs
echo "2. Insert jobs:"
curl -X POST "$API_URL/data/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"id": 1, "job": "Software Engineer"},
      {"id": 2, "job": "Sales Manager"}
    ]
  }'
echo -e "\n"

# Test backup
echo "3. Backup departments:"
curl -X POST "$API_URL/backup/departments"
echo -e "\n"

# Test validation error
echo "4. Test validation (should fail):"
curl -X POST "$API_URL/data/departments" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"department": "Missing ID"}
    ]
  }'
echo -e "\n"
