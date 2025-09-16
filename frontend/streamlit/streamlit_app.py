import streamlit as st
import requests
import json
import pandas as pd
import os

# Configuration from environment variables
DATA_API_URL = os.environ.get('DATA_API_URL', 'https://euvoczmkf2.execute-api.us-east-1.amazonaws.com/Prod')
BEDROCK_API_URL = os.environ.get('BEDROCK_API_URL', 'https://k86bczfnj3.execute-api.us-east-1.amazonaws.com/Prod')

def execute_sql(sql_query):
    """Execute SQL query via API"""
    return requests.post(f"{DATA_API_URL}/sql", json={"sql": sql_query})

def insert_data(table, data):
    """Insert data via API"""
    return requests.post(f"{DATA_API_URL}/data/{table}", json={"data": data})

def ask_bedrock(question):
    """Ask Bedrock AI a question"""
    return requests.post(f"{BEDROCK_API_URL}/ask", json={"question": question})

def query_data_page():
    """Query Data page"""
    st.header("🔍 Query Data")
    
    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Show All Departments"):
            response = execute_sql("SELECT * FROM hr_data.departments")
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data['rows'], columns=data['columns'])
                st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
    
    with col2:
        if st.button("Show All Jobs"):
            response = execute_sql("SELECT * FROM hr_data.jobs")
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data['rows'], columns=data['columns'])
                st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
    
    with col3:
        if st.button("Show All Employees"):
            response = execute_sql("SELECT e.id, e.name, e.datetime, d.department, j.job FROM hr_data.hired_employees e LEFT JOIN hr_data.departments d ON e.department_id = d.id LEFT JOIN hr_data.jobs j ON e.job_id = j.id")
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data['rows'], columns=data['columns'])
                st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
    
    # Custom SQL
    st.subheader("Custom SQL Query")
    sql_query = st.text_area("Enter SQL query:", value="SELECT * FROM hr_data.departments LIMIT 10", height=100)
    
    if st.button("Execute SQL"):
        if sql_query:
            response = execute_sql(sql_query)
            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    st.error(f"SQL Error: {data['error']}")
                else:
                    df = pd.DataFrame(data['rows'], columns=data['columns'])
                    st.dataframe(df, use_container_width=True)
                    st.info(f"Returned {data['count']} rows")
            else:
                try:
                    error_data = response.json()
                    st.error(f"Query failed: {error_data}")
                except:
                    st.error(f"Query failed: Status {response.status_code} - {response.text}")

def insert_data_page():
    """Insert Data page"""
    st.header("📝 Insert New Data")
    
    # Batch insert option
    insert_mode = st.radio("Insert Mode:", ["Single Record", "Batch Insert (up to 1000 records)"])
    
    table_type = st.selectbox("Select table:", ["departments", "jobs", "hired_employees"])
    
    if insert_mode == "Single Record":
        if table_type == "departments":
            st.subheader("Add Department")
            dept_id = st.number_input("Department ID", min_value=1, step=1)
            dept_name = st.text_input("Department Name")
            
            if st.button("Add Department"):
                if dept_name:
                    data = [{"id": int(dept_id), "department": dept_name}]
                    response = insert_data("departments", data)
                    if response.status_code == 200:
                        st.success("Department added successfully!")
                    else:
                        st.error(f"Error: {response.text}")
        
        elif table_type == "jobs":
            st.subheader("Add Job")
            job_id = st.number_input("Job ID", min_value=1, step=1)
            job_name = st.text_input("Job Title")
            
            if st.button("Add Job"):
                if job_name:
                    data = [{"id": int(job_id), "job": job_name}]
                    response = insert_data("jobs", data)
                    if response.status_code == 200:
                        st.success("Job added successfully!")
                    else:
                        st.error(f"Error: {response.text}")
        
        elif table_type == "hired_employees":
            st.subheader("Add Employee")
            emp_id = st.number_input("Employee ID", min_value=1, step=1)
            emp_name = st.text_input("Employee Name")
            dept_id = st.number_input("Department ID", min_value=1, step=1)
            job_id = st.number_input("Job ID", min_value=1, step=1)
            
            if st.button("Add Employee"):
                if emp_name:
                    data = [{
                        "id": int(emp_id),
                        "name": emp_name,
                        "department_id": int(dept_id),
                        "job_id": int(job_id)
                    }]
                    response = insert_data("hired_employees", data)
                    if response.status_code == 200:
                        st.success("Employee added successfully!")
                    else:
                        st.error(f"Error: {response.text}")
    
    else:  # Batch Insert
        st.subheader(f"Batch Insert - {table_type.title()}")
        st.info("Enter JSON array with 1-1000 records. Duplicates will be prevented by primary key constraints.")
        
        if table_type == "departments":
            example_data = '''[
  {"id": 1, "department": "Engineering"},
  {"id": 2, "department": "Marketing"},
  {"id": 3, "department": "Sales"}
]'''
        elif table_type == "jobs":
            example_data = '''[
  {"id": 1, "job": "Software Engineer"},
  {"id": 2, "job": "Data Scientist"},
  {"id": 3, "job": "Product Manager"}
]'''
        else:  # hired_employees
            example_data = '''[
  {"id": 1, "name": "John Doe", "department_id": 1, "job_id": 1},
  {"id": 2, "name": "Jane Smith", "department_id": 2, "job_id": 2},
  {"id": 3, "name": "Bob Johnson", "department_id": 1, "job_id": 3}
]'''
        
        batch_data = st.text_area(
            "JSON Data (1-1000 records):", 
            value=example_data,
            height=200,
            help="Enter a JSON array of objects. Each object represents one record."
        )
        
        if st.button("Insert Batch Data"):
            try:
                data = json.loads(batch_data)
                
                if not isinstance(data, list):
                    st.error("Data must be a JSON array")
                elif len(data) == 0:
                    st.error("Data array cannot be empty")
                elif len(data) > 1000:
                    st.error("Maximum 1000 records allowed per batch")
                else:
                    response = insert_data(table_type, data)
                    if response.status_code == 200:
                        st.success(f"Successfully inserted {len(data)} records!")
                    else:
                        st.error(f"Error: {response.text}")
                        
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format: {str(e)}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def backup_restore_page():
    """Backup & Restore page"""
    st.header("💾 Data Backup & Restore")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create Backup")
        backup_table = st.selectbox("Select table to backup:", ["departments", "jobs", "hired_employees"])
        
        if st.button("Create AVRO Backup"):
            with st.spinner(f"Creating backup for {backup_table}..."):
                response = requests.post(f"{DATA_API_URL}/backup/{backup_table}")
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Backup created successfully!")
                    st.info(f"📁 Backup key: `{result['backup_key']}`")
                    st.code(f"s3://{result['backup_key']}")
                else:
                    st.error(f"❌ Backup failed: {response.text}")
    
    with col2:
        st.subheader("Restore from Backup")
        restore_table = st.selectbox("Select table to restore:", ["departments", "jobs", "hired_employees"], key="restore_table")
        backup_key = st.text_input("Backup Key:", placeholder="backups/departments/2024-01-01T12:00:00.avro")
        
        if st.button("Restore from Backup"):
            if not backup_key:
                st.error("Please enter a backup key")
            else:
                with st.spinner(f"Restoring {restore_table} from backup..."):
                    response = requests.post(
                        f"{DATA_API_URL}/restore/{restore_table}",
                        json={"backup_key": backup_key}
                    )
                    
                    if response.status_code == 200:
                        st.success(f"✅ Table {restore_table} restored successfully!")
                    else:
                        st.error(f"❌ Restore failed: {response.text}")

def hr_reports_page():
    """HR Reports page"""
    st.header("📊 HR Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Quarterly Hiring Report")
        year_q = st.selectbox("Select Year:", [2020, 2021, 2022, 2023, 2024], index=1, key="year_q")
        
        if st.button("Generate Quarterly Report"):
            response = requests.get(f"{DATA_API_URL}/reports/quarterly_hiring_report/{year_q}")
            if response.status_code == 200:
                data = response.json()
                if data['rows']:
                    st.markdown(f"### Quarterly Hiring Report - {year_q}")
                    df = pd.DataFrame(data['rows'], columns=data['columns'])
                    st.dataframe(df, use_container_width=True)
                    st.info(f"Total records: {len(data['rows'])}")
                else:
                    st.warning(f"No hiring data found for {year_q}")
            else:
                st.error(f"Error: {response.text}")
    
    with col2:
        st.subheader("Departments Above Average Hiring")
        year_d = st.selectbox("Select Year:", [2020, 2021, 2022, 2023, 2024], index=1, key="year_d")
        
        if st.button("Generate Department Report"):
            response = requests.get(f"{DATA_API_URL}/reports/departments_above_avg_hiring/{year_d}")
            if response.status_code == 200:
                data = response.json()
                if data['rows']:
                    st.markdown(f"### Departments Above Average Hiring - {year_d}")
                    df = pd.DataFrame(data['rows'], columns=data['columns'])
                    st.dataframe(df, use_container_width=True)
                    st.info(f"Total departments above average: {len(data['rows'])}")
                else:
                    st.warning(f"No departments above average for {year_d}")
            else:
                st.error(f"Error: {response.text}")

def ask_ai_page():
    """Ask AI page"""
    st.header("🤖 Ask AI About HR Data")
    
    # Sample questions
    st.subheader("Sample Questions")
    sample_questions = [
        "How many employees were hired in 2021?",
        "Which department has the most employees?",
        "Show me the top 5 job titles by employee count",
        "What's the hiring trend by quarter in 2021?"
    ]
    
    for i, question in enumerate(sample_questions):
        if st.button(f"📝 {question}", key=f"sample_{i}"):
            st.session_state.ai_question = question
    
    # Custom question input
    question = st.text_area(
        "Ask a question about HR data:",
        value=st.session_state.get('ai_question', ''),
        height=100,
        help="Ask questions about employees, departments, jobs, hiring trends, etc."
    )
    
    if st.button("🚀 Ask AI"):
        if question:
            with st.spinner("AI is analyzing your question..."):
                response = ask_bedrock(question)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'sql_query' in result:
                        st.subheader("Generated SQL Query")
                        st.code(result['sql_query'], language='sql')
                    
                    if 'data' in result and result['data']:
                        st.subheader("Query Results")
                        df = pd.DataFrame(result['data']['rows'], columns=result['data']['columns'])
                        st.dataframe(df, use_container_width=True)
                        st.info(f"Found {result['data']['count']} results")
                    
                    if 'answer' in result:
                        st.subheader("AI Analysis")
                        st.write(result['answer'])
                else:
                    st.error(f"Error: {response.text}")
        else:
            st.warning("Please enter a question")

def main():
    st.set_page_config(
        page_title="HR Data Management System",
        page_icon="👥",
        layout="wide"
    )
    
    st.title("👥 HR Data Management System")
    st.markdown("Complete serverless HR data management with REST APIs, AI-powered queries, and web interface.")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Query Data", "Insert Data", "Backup & Restore", "HR Reports", "Ask AI"]
    )
    
    # Page routing
    if page == "Query Data":
        query_data_page()
    elif page == "Insert Data":
        insert_data_page()
    elif page == "Backup & Restore":
        backup_restore_page()
    elif page == "HR Reports":
        hr_reports_page()
    elif page == "Ask AI":
        ask_ai_page()

if __name__ == "__main__":
    main()
