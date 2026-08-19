MODEL (
  name gold.fct_risk_metrics,
  kind FULL,
  audits (
    not_null(columns := (id_pol)),
    accepted_range(column := loss_ratio, min_v := 0, max_v := 1000000)
  )
);

SELECT
  fp.id_pol,
  fp.policyholder_key,
  fp.vehicle_key,
  fp.region_key,
  20240101                                        AS date_key,
  fp.exposure,
  COALESCE(fc.claim_count, 0)                     AS claim_count,
  COALESCE(fc.claim_amount, 0)                    AS claim_amount,
  fp.earned_premium,
  COALESCE(fc.claim_count, 0) / NULLIF(fp.exposure, 0)                    AS frequency,
  COALESCE(fc.claim_amount, 0) / NULLIF(fc.claim_count, 0)               AS severity,
  (COALESCE(fc.claim_count, 0) / NULLIF(fp.exposure, 0))
    * (COALESCE(fc.claim_amount, 0) / NULLIF(fc.claim_count, 0))         AS pure_premium,
  COALESCE(fc.claim_amount, 0) / NULLIF(fp.earned_premium, 0)            AS loss_ratio
FROM gold.fct_policies AS fp
LEFT JOIN gold.fct_claims AS fc
  ON fp.id_pol = fc.id_pol