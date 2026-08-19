MODEL (
  name gold.dim_date,
  kind FULL
);

SELECT
  CAST(d AS DATE)                        AS full_date,
  CAST(TO_CHAR(d, 'YYYYMMDD') AS INTEGER) AS date_key,
  EXTRACT(YEAR    FROM d)                AS year,
  EXTRACT(QUARTER FROM d)                AS quarter,
  EXTRACT(MONTH   FROM d)                AS month
FROM (
  SELECT DATEADD(DAY, SEQ4(), DATE '2024-01-01') AS d
  FROM TABLE(GENERATOR(ROWCOUNT => 366))
)