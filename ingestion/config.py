from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"

# Identifiants OpenML des deux tables freMTPL2
OPENML_FREQ_ID = 41214   
OPENML_SEV_ID = 41215   

# Noms des fichiers Parquet de sortie
POLICIES_PARQUET = DATA_RAW / "policies.parquet"
CLAIMS_PARQUET = DATA_RAW / "claims.parquet"