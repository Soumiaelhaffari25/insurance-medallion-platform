MODEL (
  name silver.stg_policies,
  kind VIEW,
  audits (
    not_null(columns := (id_pol)),
    unique_values(columns := (id_pol)),
    accepted_range(column := exposure, min_v := 0, max_v := 1),
    accepted_range(column := driver_age, min_v := 18, max_v := 99)
  )
);

SELECT
  CAST(IDpol AS BIGINT)                          AS id_pol,
  CAST(ClaimNb AS INTEGER)                        AS claim_nb,
  LEAST(CAST(Exposure AS DOUBLE), 1.0)           AS exposure,
  CAST(Area AS VARCHAR)                           AS area,
  CAST(VehPower AS INTEGER)                       AS veh_power,
  CAST(VehAge AS INTEGER)                         AS veh_age,
  CAST(DrivAge AS INTEGER)                        AS driver_age,
  CAST(BonusMalus AS INTEGER)                     AS bonus_malus,
  CAST(VehBrand AS VARCHAR)                       AS veh_brand,
  REPLACE(CAST(VehGas AS VARCHAR), '''', '')     AS veh_gas,
  CAST(Density AS INTEGER)                        AS density,
  CAST(Region AS VARCHAR)                         AS region
FROM bronze.raw_policies
WHERE Exposure > 0
  AND DrivAge BETWEEN 18 AND 99