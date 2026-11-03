SELECT
  run_id,
  model,
  COUNTIF(error IS NULL) AS answered,
  COUNTIF(error IS NULL AND correct) AS strict_correct,
  COUNTIF(error IS NULL AND lenient_correct AND NOT correct) AS format_failures,
  ROUND(100 * SAFE_DIVIDE(
    COUNTIF(error IS NULL AND lenient_correct AND NOT correct),
    COUNTIF(error IS NULL)), 1) AS format_tax_pct
FROM `green-llm-observatory.observatory.responses`
GROUP BY run_id, model
ORDER BY model, run_id;