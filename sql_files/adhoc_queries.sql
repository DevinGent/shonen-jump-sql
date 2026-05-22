-- This file is for adhoc database queries.

SELECT * FROM dates ORDER BY date DESC LIMIT 8;

SELECT series, AVG(toc_rank) AS average_toc FROM chapters GROUP BY series
ORDER BY average_toc;

WITH latest_dates AS (
SELECT date FROM dates ORDER BY date DESC LIMIT 8),

eight_latest AS (
SELECT series, toc_rank, date FROM 
latest_dates LEFT JOIN chapters ON date=release_date)

SELECT series, AVG(toc_rank) AS average_toc FROM eight_latest GROUP BY series
ORDER BY average_toc;

SELECT * FROM chapters WHERE series="Me & Roboco" ORDER BY release_date;