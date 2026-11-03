SELECT
  model,
  COUNT(*) AS total_calls,
  COUNTIF(correct) AS strict_correct,
  COUNTIF(lenient_correct) AS lenient_correct,
  COUNTIF(lenient_correct) - COUNTIF(correct) AS format_failures,
  ROUND(100 * (COUNTIF(lenient_correct) - COUNTIF(correct)) / COUNT(*), 1) AS format_tax_pct
FROM `green-llm-observatory.observatory.responses`
GROUP BY model
ORDER BY format_tax_pct DESC;
