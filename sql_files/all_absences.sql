-- Combines the results of both the absences and hiatuses tables.

SELECT * FROM absences
UNION
SELECT DISTINCT hiatuses.series, chapters.release_date FROM hiatuses LEFT JOIN chapters
ON (chapters.release_date BETWEEN hiatuses.start_date AND hiatuses.end_date);

