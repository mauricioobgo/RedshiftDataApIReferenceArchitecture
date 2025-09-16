import json
import os
import boto3
from datetime import datetime
from typing import List, Dict, Any
import fastavro
import io

# Environment variables
SECRET_NAME = os.environ['SECRET_NAME']
REDSHIFT_HOST = os.environ['REDSHIFT_HOST']
REDSHIFT_DB = os.environ['REDSHIFT_DB']
S3_BUCKET = os.environ['S3_BUCKET']

# Initialize clients
redshift_data = boto3.client('redshift-data')
s3_client = boto3.client('s3')
secrets_client = boto3.client('secretsmanager')

def get_db_credentials():
    """Get database credentials from Secrets Manager"""
    secret = secrets_client.get_secret_value(SecretId=SECRET_NAME)
    return json.loads(secret['SecretString'])

def execute_sql_query(sql_query):
    """Execute SQL query using Redshift Data API"""
    try:
        credentials = get_db_credentials()
        
        response = redshift_data.execute_statement(
            ClusterIdentifier=REDSHIFT_HOST.split('.')[0],
            Database=REDSHIFT_DB,
            DbUser=credentials['username'],
            Sql=sql_query
        )
        
        query_id = response['Id']
        
        # Wait for query completion
        while True:
            status_response = redshift_data.describe_statement(Id=query_id)
            status = status_response['Status']
            
            if status == 'FINISHED':
                break
            elif status in ['FAILED', 'ABORTED']:
                error = status_response.get('Error', 'Unknown error')
                raise Exception(f"Query failed: {error}")
        
        # Check if query has results (SELECT queries)
        has_result_set = status_response.get('HasResultSet', False)
        
        if has_result_set:
            # Get results for SELECT queries
            result_response = redshift_data.get_statement_result(Id=query_id)
            
            # Format results
            columns = [col['name'] for col in result_response['ColumnMetadata']]
            rows = []
            
            for record in result_response['Records']:
                row = []
                for field in record:
                    if 'stringValue' in field:
                        row.append(field['stringValue'])
                    elif 'longValue' in field:
                        row.append(field['longValue'])
                    elif 'doubleValue' in field:
                        row.append(field['doubleValue'])
                    elif 'booleanValue' in field:
                        row.append(field['booleanValue'])
                    elif 'isNull' in field:
                        row.append(None)
                    else:
                        row.append(str(field))
                rows.append(row)
            
            return {
                'columns': columns,
                'rows': rows,
                'count': len(rows)
            }
        else:
            # For INSERT, UPDATE, DELETE queries - return success status
            return {
                'columns': [],
                'rows': [],
                'count': 0,
                'message': 'Query executed successfully'
            }
        
    except Exception as e:
        raise Exception(f"Database query error: {str(e)}")

def validate_departments(data: List[Dict]) -> List[str]:
    errors = []
    for i, row in enumerate(data):
        if not row.get('id') or not isinstance(row['id'], int):
            errors.append(f"Row {i}: id is required and must be integer")
        if not row.get('department') or len(row['department']) > 255:
            errors.append(f"Row {i}: department is required and max 255 chars")
    return errors

def validate_jobs(data: List[Dict]) -> List[str]:
    errors = []
    for i, row in enumerate(data):
        if not row.get('id') or not isinstance(row['id'], int):
            errors.append(f"Row {i}: id is required and must be integer")
        if not row.get('job') or len(row['job']) > 255:
            errors.append(f"Row {i}: job is required and max 255 chars")
    return errors

def validate_hired_employees(data: List[Dict]) -> List[str]:
    errors = []
    for i, row in enumerate(data):
        if not row.get('id') or not isinstance(row['id'], int):
            errors.append(f"Row {i}: id is required and must be integer")
        if not row.get('name') or len(row['name']) > 255:
            errors.append(f"Row {i}: name is required and max 255 chars")
    return errors

def insert_batch_data(table: str, data: List[Dict]):
    """Insert batch data using Redshift Data API"""
    
    # Build INSERT statement
    if table == 'departments':
        columns = ['id', 'department']
    elif table == 'jobs':
        columns = ['id', 'job']
    elif table == 'hired_employees':
        columns = ['id', 'name', 'datetime', 'department_id', 'job_id']
    else:
        raise ValueError(f"Invalid table: {table}")
    
    # Generate VALUES clause
    values_list = []
    for record in data:
        if table == 'hired_employees' and 'datetime' not in record:
            record['datetime'] = 'CURRENT_TIMESTAMP'
        
        values = []
        for col in columns:
            if col == 'datetime' and record.get(col) == 'CURRENT_TIMESTAMP':
                values.append('CURRENT_TIMESTAMP')
            else:
                value = record.get(col, 'NULL')
                if value is None or value == 'NULL':
                    values.append('NULL')
                elif isinstance(value, str):
                    values.append(f"'{value.replace(chr(39), chr(39)+chr(39))}'")
                else:
                    values.append(str(value))
        values_list.append(f"({', '.join(values)})")
    
    sql = f"""
    INSERT INTO hr_data.{table} ({', '.join(columns)})
    VALUES {', '.join(values_list)}
    """
    
    execute_sql_query(sql)

def backup_table(table: str):
    """Backup table to S3 in AVRO format using Redshift Data API"""
    
    # Get table data
    result = execute_sql_query(f"SELECT * FROM hr_data.{table}")
    
    # Convert to AVRO format
    if result['rows']:
        # Create AVRO schema
        fields = []
        for col in result['columns']:
            fields.append({"name": col, "type": ["null", "string"]})
        
        schema = {
            "type": "record",
            "name": table,
            "fields": fields
        }
        
        # Convert rows to records
        records = []
        for row in result['rows']:
            record = {}
            for i, col in enumerate(result['columns']):
                record[col] = str(row[i]) if row[i] is not None else None
            records.append(record)
        
        # Write to AVRO
        buffer = io.BytesIO()
        fastavro.writer(buffer, schema, records)
        buffer.seek(0)
        
        backup_key = f"backups/{table}/{datetime.now().isoformat()}.avro"
        s3_client.put_object(Bucket=S3_BUCKET, Key=backup_key, Body=buffer.getvalue())
        
        return backup_key
    else:
        raise Exception(f"No data found in table {table}")

def restore_table(table: str, backup_key: str):
    """Restore table from S3 AVRO backup using Redshift Data API"""
    
    # Get backup from S3
    response = s3_client.get_object(Bucket=S3_BUCKET, Key=backup_key)
    buffer = io.BytesIO(response['Body'].read())
    
    # Read AVRO data
    records = []
    for record in fastavro.reader(buffer):
        records.append(record)
    
    if records:
        # Clear existing data first
        delete_sql = f"DELETE FROM hr_data.{table}"
        execute_sql_query(delete_sql)
        
        # Insert backup data in smaller batches
        columns = list(records[0].keys())
        batch_size = 100  # Process in smaller batches
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            values_list = []
            
            for record in batch:
                values = []
                for col in columns:
                    value = record.get(col)
                    if value is None:
                        values.append('NULL')
                    elif isinstance(value, str):
                        values.append(f"'{value.replace(chr(39), chr(39)+chr(39))}'")
                    else:
                        values.append(str(value))
                values_list.append(f"({', '.join(values)})")
            
            if values_list:  # Only execute if we have data
                sql = f"""
                INSERT INTO hr_data.{table} ({', '.join(columns)})
                VALUES {', '.join(values_list)}
                """
                execute_sql_query(sql)

def execute_report_query(query_name: str, year: int) -> Dict[str, Any]:
    """Execute predefined report queries using Redshift Data API"""
    
    query_templates = {
        'quarterly_hiring_report': f"""
            SELECT 
                d.department,
                j.job,
                SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 1 THEN 1 ELSE 0 END) AS Q1,
                SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 2 THEN 1 ELSE 0 END) AS Q2,
                SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 3 THEN 1 ELSE 0 END) AS Q3,
                SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 4 THEN 1 ELSE 0 END) AS Q4
            FROM hr_data.hired_employees e
            JOIN hr_data.departments d ON e.department_id = d.id
            JOIN hr_data.jobs j ON e.job_id = j.id
            WHERE EXTRACT(YEAR FROM e.datetime) = {year}
            GROUP BY d.department, j.job
            ORDER BY d.department, j.job
        """,
        'departments_above_avg_hiring': f"""
            WITH CTE1 AS (
                SELECT
                    d.id AS department_id,
                    d.department AS department_name,
                    COUNT(DISTINCT e.id) AS hired,
                    AVG(COUNT(DISTINCT e.id)) OVER() AS avg_hired
                FROM hr_data.hired_employees e
                JOIN hr_data.departments d ON e.department_id = d.id
                WHERE EXTRACT(YEAR FROM e.datetime) = {year}
                    AND d.department IS NOT NULL
                GROUP BY d.id, d.department
            )
            SELECT 
                department_id,
                department_name,
                hired,
                ROUND(avg_hired, 2) AS avg_hired
            FROM CTE1
            WHERE hired > avg_hired
            ORDER BY hired DESC
        """
    }
    
    query = query_templates.get(query_name)
    if not query:
        raise ValueError(f"Unknown query: {query_name}")
    
    return execute_sql_query(query)

def lambda_handler(event, context):
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    try:
        method = event['httpMethod']
        path = event['path']
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        # Handle OPTIONS request for CORS
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        if method == 'POST' and path.startswith('/data/'):
            table = path.split('/')[-1]
            data = body.get('data', [])
            
            if not data or len(data) > 1000:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Data must contain 1-1000 rows'})
                }
            
            # Validate data
            if table == 'departments':
                errors = validate_departments(data)
            elif table == 'jobs':
                errors = validate_jobs(data)
            elif table == 'hired_employees':
                errors = validate_hired_employees(data)
            else:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Invalid table name'})
                }
            
            if errors:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'errors': errors})
                }
            
            insert_batch_data(table, data)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': f'Inserted {len(data)} rows into {table}'})
            }
        
        elif method == 'POST' and path.startswith('/backup/'):
            table = path.split('/')[-1]
            backup_key = backup_table(table)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': f'Backup created', 'backup_key': backup_key})
            }
        
        elif method == 'POST' and path.startswith('/restore/'):
            table = path.split('/')[-1]
            backup_key = body.get('backup_key')
            if not backup_key:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'backup_key is required'})
                }
            
            restore_table(table, backup_key)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': f'Table {table} restored from {backup_key}'})
            }
        
        elif method == 'POST' and path == '/sql':
            # Execute custom SQL
            sql_query = body.get('sql', '')
            
            if not sql_query:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'SQL query is required'})
                }
            
            try:
                result = execute_sql_query(sql_query)
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(result)
                }
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': str(e)})
                }
        
        elif method == 'GET' and path.startswith('/reports/'):
            # Handle report endpoints
            path_parts = path.strip('/').split('/')
            print(f"DEBUG: path_parts = {path_parts}")  # Debug logging
            
            if len(path_parts) >= 3:
                report_type = path_parts[1]  # This should be the report name
                year = path_parts[2]         # This should be the year
            else:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': f'Invalid path format. Expected /reports/report_type/year, got {path}'})
                }
            
            print(f"DEBUG: report_type = {report_type}, year = {year}")  # Debug logging
            
            # Validate year
            try:
                year_int = int(year)
                if year_int < 2020 or year_int > 2030:
                    raise ValueError("Year must be between 2020 and 2030")
            except ValueError as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': f'Invalid year parameter: {str(e)}'})
                }
            
            # Execute report query
            try:
                print(f"DEBUG: Executing query {report_type} for year {year_int}")  # Debug logging
                result = execute_report_query(report_type, year_int)
                print(f"DEBUG: Query result: {result}")  # Debug logging
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(result)
                }
            except ValueError as e:
                print(f"DEBUG: ValueError: {str(e)}")  # Debug logging
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({'error': str(e)})
                }
            except Exception as e:
                print(f"DEBUG: Exception: {str(e)}")  # Debug logging
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({'error': f'Query execution failed: {str(e)}'})
                }
        
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
