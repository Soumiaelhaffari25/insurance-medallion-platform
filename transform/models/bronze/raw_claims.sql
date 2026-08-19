MODEL (
  name bronze.raw_claims,
  kind VIEW
);

SELECT
  IDPOL        AS IDpol,
  CLAIMAMOUNT  AS ClaimAmount,
  LOADED_AT    AS _loaded_at,
  SOURCE_FILE  AS _source_file
FROM INSURANCE.RAW.CLAIMS