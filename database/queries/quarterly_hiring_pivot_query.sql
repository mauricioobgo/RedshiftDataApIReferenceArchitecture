-- Redshift-compatible pivot query for quarterly hiring report
-- Redshift doesn't support PIVOT syntax, so we use conditional aggregation

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
WHERE EXTRACT(YEAR FROM e.datetime) = 2021
GROUP BY d.department, j.job
ORDER BY d.department, j.job;
