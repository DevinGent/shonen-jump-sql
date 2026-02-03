-- Machine Learning Prep 2

SELECT title, total_chapters, status FROM debuts
LEFT JOIN series ON series.title=debuts.series
ORDER BY total_chapters