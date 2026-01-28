SELECT title, total_chapters, status FROM debuts LEFT JOIN series ON title=series
WHERE total_chapters>40 OR status ='Complete' OR title in ('Harukaze Mound','Otr of the Flame')
ORDER BY total_chapters;

SELECT title, total_chapters, status FROM debuts LEFT JOIN series ON title=series
WHERE (total_chapters>40 OR status ='Complete' OR title in ('Harukaze Mound','Otr of the Flame')) 
AND total_chapters>50 
ORDER BY total_chapters;

SELECT title, total_chapters, status FROM debuts LEFT JOIN series ON title=series
WHERE (total_chapters>40 OR status ='Complete' OR title in ('Harukaze Mound','Otr of the Flame')) 
AND total_chapters>50 AND (total_chapters<100 OR status='Ongoing')
ORDER BY total_chapters;

SELECT title, total_chapters, status FROM debuts LEFT JOIN series ON title=series
WHERE status ='Ongoing'
ORDER BY total_chapters;

SELECT title, total_chapters, release_date FROM finales LEFT JOIN series ON title=series
WHERE release_date>'2024-12-30'
ORDER BY total_chapters;
