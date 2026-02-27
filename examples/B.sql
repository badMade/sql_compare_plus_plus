-- Example B (same semantics under canonicalization)
SELECT a, SUM(x) AS sx, b
FROM t1 JOIN t2 ON t2.id = t1.id
WHERE x=1 AND y=2;
