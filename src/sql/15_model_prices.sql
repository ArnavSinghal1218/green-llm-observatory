CREATE OR REPLACE TABLE `green-llm-observatory.observatory.model_prices` (
  model STRING,
  effective_from DATE,
  input_usd_per_1m FLOAT64,
  output_usd_per_1m FLOAT64,
  checked_on DATE,
  source_url STRING
);

INSERT INTO `green-llm-observatory.observatory.model_prices` VALUES
  ('gemini-3.1-flash-lite', DATE '2026-11-01', 0.25, 1.50, DATE '2026-11-03',
   'https://ai.google.dev/gemini-api/docs/pricing'),
  ('gemini-3.5-flash-lite', DATE '2026-11-01', 0.30, 2.50, DATE '2026-11-03',
   'https://ai.google.dev/gemini-api/docs/pricing');