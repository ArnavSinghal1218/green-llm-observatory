SELECT
  model,
  prompt_id,
  COUNT(*) AS calls,
  COUNTIF(error IS NOT NULL) AS failed,
  MAX(SUBSTR(error, 1, 20)) AS error_type,
  ROUND(MAX(total_latency_s), 0) AS worst_s
FROM `green-llm-observatory.observatory.responses`
WHERE run_id = '20261109T094222Z'
GROUP BY model, prompt_id
HAVING COUNTIF(error IS NOT NULL) > 0
ORDER BY failed DESC, model;