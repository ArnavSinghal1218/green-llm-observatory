
SELECT
  model,
  SUM(input_tokens) AS input,
  SUM(output_tokens) AS output,
  SUM(thought_tokens) AS thought,
  SUM(total_tokens) AS total,
  ROUND(100 * SAFE_DIVIDE(SUM(thought_tokens), SUM(total_tokens)), 1) AS thought_pct
FROM `green-llm-observatory.observatory.responses`
GROUP BY model
ORDER BY thought_pct DESC;