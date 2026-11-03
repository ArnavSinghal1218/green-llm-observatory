SELECT
  model,
  COUNT(*) AS calls,
  COUNTIF(correct) AS strict_correct,
  COUNTIF(lenient_correct) AS lenient_correct,
  ROUND(AVG(total_tokens), 1) AS avg_tokens
FROM `green-llm-observatory.observatory.responses`
GROUP BY model
ORDER BY avg_tokens;
