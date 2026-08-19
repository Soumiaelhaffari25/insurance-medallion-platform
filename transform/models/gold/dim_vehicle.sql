MODEL (
  name gold.dim_vehicle,
  kind FULL,
  audits (
    unique_values(columns := (vehicle_key)),
    not_null(columns := (vehicle_key))
  )
);

SELECT DISTINCT
  HASH(veh_brand, veh_power, veh_age, veh_gas) AS vehicle_key,
  veh_brand   AS brand,
  veh_power   AS power,
  veh_age     AS vehicle_age,
  veh_gas     AS fuel_type
FROM silver.stg_policies