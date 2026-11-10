-- monthly revenue per region with running total
WITH monthly AS (
  SELECT r.region, DATE_TRUNC('month', o.created_at) AS m,
         SUM(o.amount) AS revenue
  FROM orders o JOIN regions r ON r.id = o.region_id
  WHERE o.status = 'paid'
  GROUP BY r.region, DATE_TRUNC('month', o.created_at)
)
SELECT region, m, revenue,
       SUM(revenue) OVER (PARTITION BY region ORDER BY m) AS running_total,
       RANK() OVER (PARTITION BY m ORDER BY revenue DESC) AS rank_in_month
FROM monthly ORDER BY m, rank_in_month;
