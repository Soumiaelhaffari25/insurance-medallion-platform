MODEL (
  name gold.dim_region,
  kind FULL,
  audits (
    unique_values(columns := (region_key)),
    not_null(columns := (region_key))
  )
);

SELECT DISTINCT
  HASH(region, area, density) AS region_key,
  region,
  area,
  density
FROM silver.stg_policies