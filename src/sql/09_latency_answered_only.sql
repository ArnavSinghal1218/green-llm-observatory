SELECT
  run_id,
  model,
  COUNTIF(error IS NULL) AS answered,
  ROUND(APPROX_QUANTILES(IF(error IS NULL, total_latency_s, NULL), 100)[OFFSET(50)], 2) AS median_answered_s,
  ROUND(MAX(IF(error IS NULL, total_latency_s, NULL)), 1) AS worst_answered_s,
  ROUND(AVG(IF(error IS NULL, attempts, NULL)), 2) AS avg_attempts
FROM `green-llm-observatory.observatory.responses`
GROUP BY run_id, model
ORDER BY model, run_id;