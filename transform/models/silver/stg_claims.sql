MODEL (
  name silver.stg_claims,
  kind VIEW,
  audits (
    not_null(columns := (id_pol)),
    accepted_range(column := claim_amount, min_v := 0, max_v := 2000000)
  )
);

SELECT
  CAST(IDpol AS BIGINT)                              AS id_pol,
  LEAST(CAST(ClaimAmount AS DOUBLE), 100000.0)       AS claim_amount
FROM bronze.raw_claims
WHERE ClaimAmount > 0