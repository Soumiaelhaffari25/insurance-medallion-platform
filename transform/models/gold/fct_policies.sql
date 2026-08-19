MODEL (
  name gold.fct_policies,
  kind FULL
);

WITH portefeuille AS (
  SELECT
    CAST((SELECT SUM(claim_nb) FROM silver.stg_policies) AS DOUBLE)
      / CAST((SELECT SUM(exposure) FROM silver.stg_policies) AS DOUBLE) AS freq_globale,
    CAST((SELECT AVG(claim_amount) FROM silver.stg_claims) AS DOUBLE)   AS severite_globale
)
SELECT
  p.id_pol,
  HASH(p.driver_age, p.bonus_malus)                    AS policyholder_key,
  HASH(p.veh_brand, p.veh_power, p.veh_age, p.veh_gas) AS vehicle_key,
  HASH(p.region, p.area, p.density)                    AS region_key,
  p.exposure,
  p.claim_nb,
  GREATEST(
    (pf.freq_globale * pf.severite_globale * p.exposure) * 1.20,
    10.0
  )                                                    AS earned_premium
FROM silver.stg_policies AS p
CROSS JOIN portefeuille AS pf