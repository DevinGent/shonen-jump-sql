-- SQLite

SELECT DISTINCT release_date, 'Blue Box' AS series_title FROM chapters WHERE release_date BETWEEN '2022-01-16' AND '2025-10-19'
EXCEPT SELECT DISTINCT release_date, 'Blue Box' AS series_title FROM chapters WHERE series='Blue Box';

SELECT * FROM chapters WHERE series='Ayashimon';

SELECT * FROM chapters WHERE release_date='2025-06-01';

SELECT * FROM chapters ORDER BY release_date DESC;

SELECT * FROM series ORDER BY status;


