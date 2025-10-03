-- Counting the number of chapters appearing in the chapters table for each series.
-- Ideally the number of expected chapters should equal the number of recorded chapters.
SELECT chapters.series, 
MAX(chapters.chapter) AS max_chapter, 
MIN(chapters.chapter) AS min_chapter,
(1+MAX(chapters.chapter)-MIN(chapters.chapter)) AS expected_chapters,
-- The following records how many chapters the series has in the chapters table (ignoring one-shots)
COUNT(chapters.series)-COALESCE(o.one_shots,0) AS recorded_reg_chapters,
o.one_shots
FROM chapters  
LEFT JOIN (SELECT series, COUNT(*) AS one_shots FROM chapters WHERE type='One-Shot'
GROUP BY series) as o
ON chapters.series=o.series
LEFT JOIN (SELECT series, COUNT(*) AS recorded_chapters FROM chapters WHERE chapter IS NOT NULL
GROUP BY series) AS c
ON chapters.series=c.series
GROUP BY chapters.series
ORDER BY chapters.series; 

-- Checking for duplicate chapters
SELECT chapters.* FROM chapters
LEFT JOIN (SELECT *,COUNT(chapter) AS dupes FROM chapters
GROUP BY series, chapter) AS d 
ON chapters.series=d.series AND chapters.chapter=d.chapter
WHERE d.dupes>1;

-- Checking for chapters with no number given.
SELECT * FROM chapters WHERE chapter IS NULL;

SELECT * FROM chapters WHERE series='Super Psychic Policeman Chojo';

