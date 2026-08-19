MODEL (
  name bronze.raw_policies,
  kind VIEW
);

SELECT
  IDPOL        AS IDpol,
  CLAIMNB      AS ClaimNb,
  EXPOSURE     AS Exposure,
  AREA         AS Area,
  VEHPOWER     AS VehPower,
  VEHAGE       AS VehAge,
  DRIVAGE      AS DrivAge,
  BONUSMALUS   AS BonusMalus,
  VEHBRAND     AS VehBrand,
  VEHGAS       AS VehGas,
  DENSITY      AS Density,
  REGION       AS Region,
  LOADED_AT    AS _loaded_at,
  SOURCE_FILE  AS _source_file
FROM INSURANCE.RAW.POLICIES