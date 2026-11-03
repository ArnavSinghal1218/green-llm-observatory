WITH per_prompt AS (
  SELECT
    model,
    COALESCE(language, 'en') AS language,
    pair_id,
    AVG(total_tokens) AS in_tokens
  FROM `green-llm-observatory.observatory.responses`
  WHERE error IS NULL AND pair_id IS NOT NULL
  GROUP BY model, language, pair_id
),
english AS (
  SELECT model, pair_id, in_tokens AS en_tokens
  FROM per_prompt
  WHERE language = 'en'
)
SELECT
  p.model,
  p.language,
  ROUND(AVG(p.in_tokens), 1) AS avg_total_tokens,
  ROUND(AVG(p.in_tokens / e.en_tokens), 2) AS ratio_vs_english
FROM per_prompt p
JOIN english e
  ON p.model = e.model AND p.pair_id = e.pair_id
GROUP BY p.model, p.language
ORDER BY p.model, p.language;