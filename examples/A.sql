-- Example A
SELECT b, a, SUM(x) AS sx
FROM t1 INNER JOIN t2 ON t1.id = t2.id
WHERE y=2 AND x=1;
