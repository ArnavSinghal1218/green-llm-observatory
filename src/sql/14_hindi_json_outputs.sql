SELECT DISTINCT model, prompt_id, output
FROM `green-llm-observatory.observatory.responses`
WHERE language = 'hi'
  AND category = 'json_extraction'
  AND error IS NULL
  AND NOT correct
ORDER BY model, prompt_id;