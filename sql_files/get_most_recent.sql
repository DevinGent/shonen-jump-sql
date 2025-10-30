-- Get the most N recent chapters from each series
-- SQLite
SELECT * FROM
(SELECT *, 
ROW_NUMBER() OVER (PARTITION BY series ORDER BY release_date DESC) as recency
FROM chapters)
-- Here we get the two most recent chapters but we can replace 2 with any choice of N we like.
WHERE recency<=2;