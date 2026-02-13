-- Displaying the table of series by status and alphabetically
SELECT * 
FROM series
-- Setting the order to be Ongoing, then Hiatus, then other. 
-- Each category should then be sorted alphabetically.
ORDER BY CASE status
WHEN 'Ongoing' THEN 1
WHEN 'Hiatus' THEN 2
ELSE 3 END,
title;