

select * from hr_data.departments_temp;
select * from hr_data.jobs_temp;
select * from hr_data.hired_employees_temp;

DROP TABLE hr_data.departments;
DROP TABLE hr_data.jobs;
DROP TABLE hr_data.hired_employees;

-- Create tables with NOT NULL constraints
CREATE TABLE hr_data.departments (
    id INTEGER NOT NULL PRIMARY KEY,
    department VARCHAR(255) NOT NULL
)
DISTSTYLE KEY
DISTKEY (id)
SORTKEY (id);

CREATE TABLE hr_data.jobs (
    id INTEGER NOT NULL PRIMARY KEY,
    job VARCHAR(255) NOT NULL
)
DISTSTYLE KEY
DISTKEY (id)
SORTKEY (id);

CREATE TABLE hr_data.hired_employees (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR(255),
    datetime TIMESTAMPTZ,
    department_id INTEGER,
    job_id INTEGER
)
DISTSTYLE KEY
DISTKEY (department_id)
SORTKEY (datetime, department_id);

-- Insert data
INSERT INTO hr_data.departments 
SELECT id, department FROM hr_data.departments_temp WHERE id IS NOT NULL;

INSERT INTO hr_data.jobs 
SELECT id, job FROM hr_data.jobs_temp WHERE id IS NOT NULL;

INSERT INTO hr_data.hired_employees 
SELECT 
    id,
    name,
    cast(datetime as TIMESTAMPTZ) as datetime,
    department_id,
    job_id
FROM hr_data.hired_employees_temp
WHERE datetime IS NOT NULL AND job_id is not null and department_id is not null
and datetime != '' AND id IS NOT NULL;

-- Add primary key constraints
ALTER TABLE hr_data.departments ADD CONSTRAINT pk_departments PRIMARY KEY (id);
ALTER TABLE hr_data.jobs ADD CONSTRAINT pk_jobs PRIMARY KEY (id);  
ALTER TABLE hr_data.hired_employees ADD CONSTRAINT pk_hired_employees PRIMARY KEY (id);

select * from hr_data.departments;
select * from hr_data.jobs;
select * from hr_data.hired_employees;
