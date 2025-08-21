-- SQLite
SELECT series.title, series.writer, s.release_date AS start_date, MAX(e.release_date) AS end_date, AVG(chapters.toc_rank) AS average_toc
FROM series 
LEFT JOIN chapters ON series.title=chapters.series
LEFT JOIN chapters AS s ON series.title=s.series AND s.chapter=1
LEFT JOIN chapters AS e ON series.title=e.series AND series.status='Complete' AND e.type !='One-Shot'
GROUP BY chapters.series
ORDER BY series.title;

SELECT series, AVG(toc_rank) as average_rank FROM chapters
GROUP BY series;

SELECT series.title, chapters.release_date AS start_date
FROM series LEFT JOIN chapters ON
series.title=chapters.series AND chapters.chapter=1;

SELECT * FROM chapters WHERE chapter IS NULL;

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
