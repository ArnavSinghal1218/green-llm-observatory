SELECT
  model,
  COALESCE(language, 'en') AS language,
  COUNTIF(list_cost_usd IS NOT NULL) AS priced_calls,
  ROUND(1000 * AVG(list_cost_usd), 4) AS usd_per_1000_calls,
  ROUND(1000 * SAFE_DIVIDE(SUM(list_cost_usd), COUNTIF(correct)), 4) AS usd_per_1000_strict_correct
FROM `green-llm-observatory.observatory.responses_costed`
WHERE error IS NULL
GROUP BY model, language
ORDER BY model, language;