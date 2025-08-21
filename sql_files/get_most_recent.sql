-- Get most recent
-- SQLite
SELECT * FROM
(SELECT *, 
ROW_NUMBER() OVER (PARTITION BY series ORDER BY release_date DESC) as recency
FROM chapters)
WHERE recency<=2;