-- This file is for adhoc database queries.

SELECT series, release_date, id, debut_or_finale,
CASE 
WHEN id-LAG(id,1,0) OVER(ORDER BY id ASC)>3 THEN 1
ELSE 0
END AS new_batch
FROM 
(SELECT series, release_date, 'Debut' AS debut_or_finale FROM debuts 
UNION SELECT series, release_date, 'Finale' AS debut_or_finale FROM finales)
LEFT JOIN dates on date=release_date
ORDER BY id ASC;

WITH batch_loc(series, release_date,date_id, debut_or_finale, new_batch) AS
(SELECT series, release_date, id, debut_or_finale,
CASE 
WHEN id-LAG(id,1,0) OVER(ORDER BY id ASC)>2 THEN 1
ELSE 0
END AS new_batch
FROM 
(SELECT series, release_date, 'Debut' AS debut_or_finale FROM debuts 
UNION SELECT series, release_date, 'Finale' AS debut_or_finale FROM finales)
LEFT JOIN dates on date=release_date
ORDER BY id ASC)

SELECT series, release_date, debut_or_finale, 
SUM(new_batch) OVER(ORDER BY release_date)
FROM batch_loc;

SELECT series, release_date, id, debut_or_finale,
CASE 
WHEN id-LAG(id,1,0) OVER(ORDER BY id ASC)>3 THEN 1
ELSE 0
END AS new_batch
FROM 
(SELECT series, release_date, 'Debut' AS debut_or_finale FROM debuts 
UNION SELECT series, release_date, 'Finale' AS debut_or_finale FROM finales)
LEFT JOIN dates on date=release_date
ORDER BY id ASC;

SELECT * FROM dates;