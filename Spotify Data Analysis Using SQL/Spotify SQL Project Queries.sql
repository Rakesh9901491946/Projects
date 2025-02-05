-- QUESTIONS - EASY LEVEL--

-- 1. Who is the senior most employee based on job title?
SELECT* FROM employee ORDER BY levels DESC LIMIT 1;

-- 2. Which countries have the most Invoices?
SELECT billing_country, COUNT(*) AS total_invoices
FROM invoice GROUP BY billing_country ORDER BY total_invoices DESC;

-- 3. What are top 3 values of total invoice?
SELECT total FROM invoice ORDER BY total DESC LIMIT 3;

-- 4. Which city has the best customers? We would like to throw a promotional Music 
-- Festival in the city we made the most money. Write a query that returns one city that
-- has the highest sum of invoice totals. Return both the city name & sum of all invoice
-- totals.

SELECT billing_city, SUM(total) AS total_invoice
FROM invoice
GROUP BY billing_city
ORDER BY total_invoice DESC
LIMIT 1;

-- 5. Who is the best customer? The customer who has spent the most money will be
-- declared the best customer. Write a query that returns the person who has spent the
-- most money.

SELECT c.customer_id, CONCAT(c.first_name," ",c.last_name) AS full_name, SUM(i.total) AS total_spend
FROM customer AS c
JOIN invoice AS i
ON c.customer_id = i.customer_id
GROUP BY c.customer_id
ORDER BY total_spend DESC
LIMIT 1;



-- MODERATE LEVEL-- QUESTIONS 

-- 1.Write query to return the email, first name, last name, & Genre of all Rock Music
-- listeners. Return your list ordered alphabetically by email starting with A

-- Method 1
SELECT DISTINCT c.customer_id, c.first_name, c.last_name, c.email
FROM customer AS c
JOIN invoice AS i ON c.customer_id = i.customer_id
JOIN invoice_line AS il ON i.invoice_id = il.invoice_id
WHERE track_id IN (SELECT t.track_id
				 FROM track AS t
                 JOIN genre AS g ON t.genre_id = g.genre_id
                 WHERE g.genre_name = 'Rock\r' )
ORDER BY c.email;

-- Method2
SELECT DISTINCT c.customer_id, c.first_name, c.last_name, c.email, g.genre_name
FROM customer AS c
JOIN invoice AS i ON c.customer_Id = i.customer_id
JOIN invoice_line AS il ON i.invoice_id = il.invoice_id
JOIN track AS t ON t.track_id = il.track_id
JOIN genre AS g ON g.genre_id = t.genre_id
WHERE g.genre_name = 'Rock\r'
ORDER BY c.email;

-- 2. Let's invite the artists who have written the most rock music in our dataset. Write a
-- query that returns the Artist name and total track count of the top 10 rock bands

SELECT a.artist_id, a.name AS artist_name, COUNT(a.name) AS total_track
FROM artist AS a
JOIN album AS albm ON albm.artist_id = a.artist_id
JOIN track AS t ON t.album_id = albm.album_id
JOIN genre AS g ON g.genre_id = t.genre_id
WHERE genre_name = 'Rock\r'
GROUP BY a.artist_id
ORDER BY total_track DESC
LIMIT 10;

-- 3. Return all the track names that have a song length longer than the average song length.
-- Return the Name and Milliseconds for each track. Order by the song length with the
-- longest songs listed first

SELECT name, milliseconds
FROM track 
WHERE milliseconds >= (SELECT AVG(milliseconds) FROM track)
ORDER BY milliseconds DESC;


-- ADVANCE LEVEL----- QUESTIONS --- 

-- 1. Find how much amount spent by each customer on artists? Write a query to return
-- customer name, artist name and total spent

WITH CTE1 AS
(SELECT artist.artist_id, artist.name AS artist_name, SUM(invoice_line.unit_price * invoice_line.quantity) AS total_sales
FROM invoice_line
JOIN track ON track.track_id = invoice_line.track_id
JOIN album ON album.album_id = track.album_id
JOIN artist ON artist.artist_id = album.artist_id
GROUP BY 1
ORDER BY total_sales DESC
LIMIT 1
)
SELECT c.customer_id, c.first_name, c.last_name, CTE1.artist_name,
SUM(il.unit_price * il.quantity) AS total_amount
FROM customer AS c
JOIN invoice AS i on c.customer_id = i.customer_id
JOIN invoice_line AS il ON i.invoice_id = il.invoice_id
JOIN track AS t ON il.track_id = t.track_id
JOIN album AS albm ON t.album_id = albm.album_id
JOIN CTE1 ON CTE1.artist_id = albm.artist_id
GROUP BY 1,2,3 
ORDER BY total_amount DESC;

-- 2. We want to find out the most popular music Genre for each country. We determine the
-- most popular genre as the genre with the highest amount of purchases. Write a query
-- that returns each country along with the top Genre. For countries where the maximum
-- number of purchases is shared return all Genres

WITH CTE1 AS
(
	SELECT c.country, g.genre_id, g.genre_name, COUNT(il.quantity) AS total_purchases,
	ROW_NUMBER() OVER(PARTITION BY c.country ORDER BY COUNT(il.quantity) DESC) AS row_no
	FROM genre AS g 
	JOIN track AS t ON t.genre_id = g.genre_id
	JOIN invoice_line AS il ON il.track_id = t.track_id
	JOIN invoice AS i ON i.invoice_id = il.invoice_id
	JOIN customer AS c ON i.customer_id = c.customer_id
	GROUP BY c.country,g.genre_id, g.genre_name
	ORDER BY c.country ASC, 1 DESC
)
SELECT* FROM CTE1 WHERE row_no <= 1;

-- 3. Write a query that determines the customer that has spent the most on music for each
-- country. Write a query that returns the country along with the top customer and how
-- much they spent. For countries where the top amount spent is shared, provide all
-- customers who spent this amount

	WITH CTE1 AS
(
	SELECT c.customer_id,c.first_name, c.last_name, i.billing_country, SUM(i.total) AS amount_spent
	FROM customer AS c
	JOIN invoice AS i ON c.customer_id = i.customer_id
	GROUP BY 1,2,3,4
	ORDER BY 1,5 DESC
),
CTE2 AS 
(
	SELECT billing_country, MAX(amount_spent) AS max_spent
	FROM CTE1 
	GROUP BY billing_country
)
SELECT CTE1.billing_country, CTE1.amount_spent, CTE1.first_name, CTE1.last_name
FROM CTE1
JOIN CTE2
ON CTE1.billing_country = CTE2.billing_country
WHERE CTE1.amount_spent = CTE2.max_spent
ORDER BY 1;







