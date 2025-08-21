-- SQLite
SELECT series.* 
FROM series
-- Setting the order to be Ongoing, then Hiatus, then other. 
-- Each category should then be sorted alphabetically.
ORDER BY CASE series.status
WHEN 'Ongoing' THEN 1
WHEN 'Hiatus' THEN 2
ELSE 3 END,
series.title;