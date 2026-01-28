-- Machine Learning Prep 1

SELECT title,genre, 
CASE
WHEN writer=artist THEN 1
ELSE 0 END one_creator,
CASE
WHEN total_chapters>=50 THEN 1
ELSE 0 END success
FROM series
WHERE total_chapters>=50 OR status="Complete";
SELECT series,COUNT(series) FROM chapters
WHERE type='Color' AND chapter<=12
GROUP BY series;
SELECT * FROM chapters
WHERE chapter<=12 AND series IN 
('Super Psychic Policeman Chojo', 'Super Smartphone', 'Tenmaku Cinema');

-- Use this one.
SELECT title,genre, 
CASE
WHEN writer=artist THEN 1
ELSE 0 END one_creator,
CASE
WHEN total_chapters>=50 THEN 1
ELSE 0 END success,
average_placement,
color_pages,
cover_pages,
debuts.release_date,
batches.added AS batch_size


FROM series
INNER JOIN debuts ON title=debuts.series
LEFT JOIN (SELECT AVG(placement) AS average_placement, series FROM chapters
WHERE chapter<=12 GROUP BY series) AS avplace
ON title=avplace.series
LEFT JOIN (SELECT series,COUNT(series) AS color_pages FROM chapters
WHERE type='Color' AND chapter<=12
GROUP BY series) AS colorp
ON title=colorp.series
LEFT JOIN (SELECT series,COUNT(series) AS cover_pages FROM chapters
WHERE type='Cover' AND chapter<=12
GROUP BY series) AS coverp
ON title=coverp.series
LEFT JOIN batches ON debuts.release_date BETWEEN batches.start_date AND batches.end_date
WHERE total_chapters>=50 OR status="Complete"
ORDER BY title;

-- Older
SELECT title,genre, 
CASE
WHEN writer=artist THEN 1
ELSE 0 END one_creator,
CASE
WHEN total_chapters>=50 THEN 1
ELSE 0 END success,
color_pages,
cover_pages


FROM series
LEFT JOIN (SELECT series,COUNT(series) AS color_pages FROM chapters
WHERE type='Color' AND chapter<=12
GROUP BY series) AS colorp
ON title=colorp.series
LEFT JOIN (SELECT series,COUNT(series) AS cover_pages FROM chapters
WHERE type='Cover' AND chapter<=12
GROUP BY series) AS coverp
ON title=coverp.series
WHERE (total_chapters>=50 OR status="Complete") AND cover_pages>=1;

SELECT * FROM chapters WHERE series="Ayashimon" ORDER BY release_date;
