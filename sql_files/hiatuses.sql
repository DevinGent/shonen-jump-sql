SELECT * FROM temp_hiatuses;

SELECT MAX(series), MIN(issue_date), MAX(issue_date),
COUNT(grouping) FROM temp_hiatuses
GROUP BY grouping
HAVING COUNT(grouping)>2;

SELECT * FROM temp_hiatuses
GROUP BY grouping
HAVING COUNT(grouping)>2;