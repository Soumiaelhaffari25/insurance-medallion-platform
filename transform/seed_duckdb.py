from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "transform" / "insurance.db"

con = duckdb.connect(str(DB_PATH))

# Schema Bronze (donnees brutes 1:1)
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

# Chargement brut + colonnes techniques (_loaded_at, _source_file)
con.execute(f"""
    CREATE OR REPLACE TABLE raw.policies AS
    SELECT *,
           now()          AS _loaded_at,
           'policies.parquet' AS _source_file
    FROM read_parquet('{(DATA_RAW / "policies.parquet").as_posix()}');
""")

con.execute(f"""
    CREATE OR REPLACE TABLE raw.claims AS
    SELECT *,
           now()        AS _loaded_at,
           'claims.parquet' AS _source_file
    FROM read_parquet('{(DATA_RAW / "claims.parquet").as_posix()}');
""")

# Verification
n_pol = con.execute("SELECT count(*) FROM raw.policies").fetchone()[0]
n_clm = con.execute("SELECT count(*) FROM raw.claims").fetchone()[0]
print(f"raw.policies : {n_pol:,} lignes")
print(f"raw.claims   : {n_clm:,} lignes")

con.close()
print(f"Base DuckDB creee : {DB_PATH}")