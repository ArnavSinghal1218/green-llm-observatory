SELECT
  prompt_id,
  ROUND(AVG(IF(model = 'gemini-3.1-flash-lite', total_tokens, NULL)), 0) AS gemini_31,
  ROUND(AVG(IF(model = 'gemini-3.5-flash-lite', total_tokens, NULL)), 0) AS gemini_35,
  ROUND(AVG(IF(model = 'gemma-4-26b-a4b-it', total_tokens, NULL)), 0) AS gemma,
  ROUND(SAFE_DIVIDE(
    AVG(IF(model = 'gemma-4-26b-a4b-it', total_tokens, NULL)),
    AVG(IF(model = 'gemini-3.1-flash-lite', total_tokens, NULL))), 1) AS gemma_vs_gemini_31
FROM `green-llm-observatory.observatory.responses`
WHERE run_id = '20261109T085230Z' AND error IS NULL
GROUP BY prompt_id
ORDER BY gemma_vs_gemini_31 DESC;