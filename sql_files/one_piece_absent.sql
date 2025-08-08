-- SQLite
-- The following SQL displays all the dates with published
-- chapters and checks whether One Piece was present or
-- absent.
SELECT a.series, b.release_date, a.type 
               FROM (SELECT DISTINCT release_date FROM chapters) AS b
               LEFT JOIN chapters AS a ON a.release_date=b.release_date
               AND a.series='One Piece';
