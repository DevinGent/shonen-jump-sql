-- This file is for adhoc database queries.
WITH colpage(series, color_pages) AS 
(SELECT series, COUNT(series) FROM chapters WHERE type='Color' AND chapter BETWEEN 8 AND 10 GROUP BY series)

SELECT series, COUNT(series) FROM chapters WHERE type='Color' AND chapter BETWEEN 8 AND 10 GROUP BY series;

SELECT * FROM chapters GROUP BY type;

SELECT debuts.*, status FROM
debuts LEFT JOIN series ON debuts.series=series.title
WHERE status='Ongoing' ORDER BY release_date;

SELECT * FROM debuts;

SELECT * FROM chapters ORDER BY release_date DESC;

SELECT * FROM debuts INNER JOIN finales ON debuts.series=finales.series;

SELECT * FROM chapters ORDER BY series;