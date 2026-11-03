CREATE OR REPLACE VIEW `green-llm-observatory.observatory.responses_costed` AS
SELECT
  r.*,
  p.input_usd_per_1m,
  p.output_usd_per_1m,
  (r.input_tokens * p.input_usd_per_1m
   + (r.output_tokens + r.thought_tokens) * p.output_usd_per_1m) / 1e6 AS list_cost_usd
FROM `green-llm-observatory.observatory.responses` AS r
LEFT JOIN `green-llm-observatory.observatory.model_prices` AS p
  ON r.model = p.model
 AND p.effective_from <= DATE(r.timestamp)
WHERE TRUE
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY r.run_id, r.repeat, r.prompt_id, r.model
  ORDER BY p.effective_from DESC
) = 1;