SELECT
  model,
  category,
  COUNT(*) AS calls,
  COUNTIF(correct) AS strict_correct,
  ROUND(100 * COUNTIF(correct) / COUNT(*), 1) AS strict_pct
FROM `green-llm-observatory.observatory.responses`
GROUP BY model, category
ORDER BY model, category;
