-- There should be 415 absences.
--First we name a selection which lists each series in the chapters table as well as their 
-- debut (or the earliest recorded date in the chapters table) and finale (or latest release date)

WITH 
series_dates(series,earliest,latest) AS(
SELECT chapters.series,
-- We select the debut if it exists or replace with the minimal date in the database if the debut is not included. 
COALESCE(debuts.release_date,(SELECT MIN(release_date) FROM chapters)) AS earliest, 
-- We follow a similar pattern for the latest release.
COALESCE(finales.release_date,(SELECT MAX(release_date) FROM chapters)) AS latest 
FROM chapters 
LEFT JOIN debuts ON chapters.series=debuts.series
LEFT JOIN finales ON chapters.series=finales.series
WHERE chapters.type!= 'One-Shot'
GROUP BY chapters.series),

all_combos(series,date) AS(SELECT * FROM
(SELECT DISTINCT series FROM chapters) 
CROSS JOIN
(SELECT DISTINCT release_date FROM chapters))

SELECT all_combos.series, date FROM all_combos
LEFT JOIN series_dates
ON all_combos.series=series_dates.series
WHERE date BETWEEN earliest AND latest
EXCEPT SELECT DISTINCT series, release_date FROM chapters;
