-- SQLite
SELECT series.title, chapters.release_date, chapters.chapter
FROM series LEFT JOIN chapters ON
series.title=chapters.series AND chapters.chapter=4;

SELECT series.title, chapters.release_date, chapters.chapter
FROM series LEFT JOIN chapters ON
series.title=chapters.series AND 
series.total_chapters=chapters.chapter AND series.genre='Sports';

SELECT series, chapter, release_date FROM chapters
WHERE series='Me & Roboco' AND release_date<'2024-04-22';

SELECT series, chapter, COUNT(*) FROM chapters
GROUP BY series, chapter
HAVING COUNT(*)>1;

SELECT * FROM chapters
WHERE series='Witch Watch' AND chapter=181;
