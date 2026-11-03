SELECT
  model,
  prompt_id,
  CASE
    WHEN error IS NOT NULL THEN 'server_error'
    WHEN STARTS_WITH(output, '```') THEN 'code_fence'
    WHEN STARTS_WITH(output, '[') THEN 'list_wrapped'
    ELSE 'wrong_answer'
  END AS failure_type,
  COUNT(*) AS times
FROM `green-llm-observatory.observatory.responses`
WHERE NOT correct
GROUP BY model, prompt_id, failure_type
ORDER BY model, prompt_id;