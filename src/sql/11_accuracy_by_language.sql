SELECT
  model,
  COALESCE(language, 'en') AS language,
  COUNTIF(error IS NULL) AS answered,
  COUNTIF(error IS NULL AND correct) AS strict_correct,
  COUNTIF(error IS NULL AND lenient_correct) AS lenient_correct,
  ROUND(100 * SAFE_DIVIDE(COUNTIF(error IS NULL AND correct), COUNTIF(error IS NULL)), 1) AS strict_pct
FROM `green-llm-observatory.observatory.responses`
GROUP BY model, language
ORDER BY model, language;