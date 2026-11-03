SELECT
  run_id,
  model,
  COUNT(*) AS calls,
  COUNTIF(error IS NOT NULL) AS failed_calls,
  COUNTIF(attempts > 1) AS needed_retry,
  ROUND(APPROX_QUANTILES(total_latency_s, 100)[OFFSET(50)], 2) AS median_s,
  ROUND(MAX(total_latency_s), 1) AS worst_s
FROM `green-llm-observatory.observatory.responses`
GROUP BY run_id, model
ORDER BY model, run_id;