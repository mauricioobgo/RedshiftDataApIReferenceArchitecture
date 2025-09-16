-- Departments with hiring above average
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
ORDER BY hired DESC;
