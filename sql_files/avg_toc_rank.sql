-- average toc rank
SELECT series.title, series.writer, s.release_date AS start_date, MAX(e.release_date) AS end_date, AVG(chapters.toc_rank) AS average_toc
FROM series 
LEFT JOIN chapters ON series.title=chapters.series
LEFT JOIN chapters AS s ON series.title=s.series AND s.chapter=1
LEFT JOIN chapters AS e ON series.title=e.series AND series.status='Complete' AND e.type !='One-Shot'
GROUP BY chapters.series
ORDER BY series.title;
