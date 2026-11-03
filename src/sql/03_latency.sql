
SELECT
  model,
  ROUND(APPROX_QUANTILES(total_latency_s, 100)[OFFSET(50)], 2) AS median_s,
  ROUND(AVG(total_latency_s), 2) AS avg_s,
  ROUND(MAX(total_latency_s), 2) AS worst_s
FROM `green-llm-observatory.observatory.responses`
GROUP BY model
ORDER BY median_s;
