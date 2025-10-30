-- SQLite

SELECT *, 'Debut' AS debut_or_finale from debuts 
UNION SELECT *, 'Finale' AS debut_or_finale FROM finales
ORDER BY release_date DESC;


