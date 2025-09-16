-- AWS Redshift DDL Statements
-- Based on CSV files from RedshiftReferenceArchitecture

-- Create departments table

CREATE TABLE hr_data.departments_temp (
    id INTEGER NOT NULL,
    department VARCHAR(255) NOT NULL
)
DISTSTYLE KEY
DISTKEY (id)
SORTKEY (id);

-- Create jobs table  
CREATE TABLE hr_data.jobs_temp (
    id INTEGER NOT NULL,
    job VARCHAR(255) NOT NULL
)
DISTSTYLE KEY
DISTKEY (id)
SORTKEY (id);

-- Create hired_employees table
CREATE TABLE hr_data.hired_employees_temp (
    id INTEGER NOT NULL,
    name VARCHAR(255) ,
    datetime VARCHAR(255),
    department_id INTEGER ,
    job_id INTEGER
)
DISTSTYLE KEY
DISTKEY (department_id)
SORTKEY (datetime, department_id);

-- Optional: Create indexes for better query performance
-- Note: Redshift uses sort keys instead of traditional indexes

-- Comments for table documentation
COMMENT ON TABLE hr_data.departments_temp IS 'Department master data';
COMMENT ON TABLE hr_data.jobs_temp IS 'Job position master data';  
COMMENT ON TABLE hr_data.hired_employees_temp IS 'Employee hiring records with department and job assignments';

COMMENT ON COLUMN hr_data.hired_employees_temp.datetime IS 'Hire datetime in ISO format';
COMMENT ON COLUMN hr_data.hired_employees_temp.department_id IS 'Foreign key reference to departments table';
COMMENT ON COLUMN hr_data.hired_employees_temp.job_id IS 'Foreign key reference to jobs table';

copy hr_data.departments_temp from 's3://aws-redshift-demo-jkashdjkahskdjhsdkj/data/departments.csv' iam_role default delimiter ',' region 'us-east-1';
copy hr_data.jobs_temp from 's3://aws-redshift-demo-jkashdjkahskdjhsdkj/data/jobs.csv' iam_role default delimiter ',' region 'us-east-1';
copy hr_data.hired_employees_temp from 's3://aws-redshift-demo-jkashdjkahskdjhsdkj/data/hired_employees.csv' iam_role default delimiter ',' region 'us-east-1';



DROP  TABLE  hr_data.departments;
DROP  TABLE  hr_data.jobs;
DROP  TABLE  hr_data.hired_employees;


select * from hr_data.departments_temp;
select * from hr_data.jobs_temp;
select * from hr_data.hired_employees_temp;

