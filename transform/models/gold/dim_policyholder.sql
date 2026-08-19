MODEL (
  name gold.dim_policyholder,
  kind FULL,
  audits (
    unique_values(columns := (policyholder_key)),
    not_null(columns := (policyholder_key))
  )
);

SELECT DISTINCT
  HASH(driver_age, bonus_malus)      AS policyholder_key,
  driver_age,
  bonus_malus,
  GREATEST(driver_age - 18, 0)       AS license_age
FROM silver.stg_policies