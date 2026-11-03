SELECT
  model,
  COALESCE(language, 'en') AS language,
  CASE
    WHEN STARTS_WITH(output, '```') THEN 'code_fence'
    WHEN STARTS_WITH(output, '[') THEN 'list_wrapped'
    ELSE 'other'
  END AS failure_type,
  COUNT(*) AS times
FROM `green-llm-observatory.observatory.responses`
WHERE error IS NULL AND NOT correct
GROUP BY model, language, failure_type
ORDER BY model, language, failure_type;