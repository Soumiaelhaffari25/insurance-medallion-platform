from sklearn.datasets import fetch_openml

from config import CLAIMS_PARQUET, DATA_RAW, OPENML_SEV_ID


def extract_claims():
    DATA_RAW.mkdir(parents=True, exist_ok=True)

    print(f"Telechargement freMTPL2sev (OpenML id={OPENML_SEV_ID})...")
    dataset = fetch_openml(data_id=OPENML_SEV_ID, as_frame=True)
    df = dataset.frame

    print(f"  -> {len(df):,} lignes de sinistres, {df.shape[1]} colonnes")
    df.to_parquet(CLAIMS_PARQUET, index=False)
    print(f"  -> ecrit dans {CLAIMS_PARQUET}")

    return df


if __name__ == "__main__":
    extract_claims()