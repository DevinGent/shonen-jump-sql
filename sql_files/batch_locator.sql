-- Batch Locator
-- SQLite
SELECT series, 
release_date,
chapter,
"start" AS start_or_end
FROM chapters WHERE chapter=1
UNION ALL
SELECT series, 
MAX(release_date),
chapter,
"end" AS start_or_end
FROM chapters
JOIN series ON series.title=chapters.series AND series.status='Complete'
GROUP BY series
ORDER BY release_date;