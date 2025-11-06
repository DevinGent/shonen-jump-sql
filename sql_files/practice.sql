-- SQLite

SELECT DISTINCT release_date, 'Blue Box' AS series_title FROM chapters WHERE release_date BETWEEN '2022-01-16' AND '2025-10-19'
EXCEPT SELECT DISTINCT release_date, 'Blue Box' AS series_title FROM chapters WHERE series='Blue Box';

SELECT * FROM chapters WHERE release_date='2024-08-25';

SELECT * FROM chapters WHERE release_date='2025-06-01';


