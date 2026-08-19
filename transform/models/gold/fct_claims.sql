MODEL (
  name gold.fct_claims,
  kind FULL
);

SELECT
  id_pol,
  COUNT(*)          AS claim_count,
  SUM(claim_amount) AS claim_amount
FROM silver.stg_claims
GROUP BY id_pol