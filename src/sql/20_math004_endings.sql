SELECT
  model,
  repeat,
  ARRAY_REVERSE(REGEXP_EXTRACT_ALL(output, r'-?\d+(?:\.\d+)?'))[SAFE_OFFSET(0)] AS last_number,
  RIGHT(output, 120) AS output_end
FROM `green-llm-observatory.observatory.responses`
WHERE run_id = '20261109T085230Z'
  AND prompt_id = 'math-004'
  AND model = 'gemini-3.5-flash-lite'
ORDER BY repeat;