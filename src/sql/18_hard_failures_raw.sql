SELECT model, prompt_id, repeat, total_tokens, SUBSTR(output, 1, 300) AS output_start
FROM `green-llm-observatory.observatory.responses`
WHERE run_id = '20261109T085230Z'
  AND error IS NULL
  AND NOT correct
  AND category IN ('reasoning', 'instruction_following')
ORDER BY model, prompt_id, repeat;