-- There should be 415 absences.

WITH 
series_dates(series,earliest,latest) AS(
SELECT chapters.series, 
COALESCE(debuts.release_date,(SELECT MIN(release_date) FROM chapters)) AS earliest, 
COALESCE(finales.release_date,(SELECT MAX(release_date) FROM chapters)) AS latest 
FROM chapters LEFT JOIN debuts ON chapters.series=debuts.series
LEFT JOIN finales ON chapters.series=finales.series
WHERE chapters.type!= 'One-Shot'
GROUP BY chapters.series),

all_dates(date) AS(SELECT DISTINCT release_date FROM chapters),

all_combos(series,date) AS(SELECT * FROM
(SELECT DISTINCT series FROM chapters) 
CROSS JOIN
(SELECT DISTINCT release_date FROM chapters))

SELECT all_combos.series, date FROM all_combos
LEFT JOIN series_dates
ON all_combos.series=series_dates.series
WHERE date BETWEEN earliest AND latest
EXCEPT SELECT DISTINCT series, release_date FROM chapters
;
