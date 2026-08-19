from sklearn.datasets import fetch_openml

from config import DATA_RAW, OPENML_FREQ_ID, POLICIES_PARQUET


def extract_policies():
    DATA_RAW.mkdir(parents=True, exist_ok=True)

    print(f"Telechargement freMTPL2freq (OpenML id={OPENML_FREQ_ID})...")
    dataset = fetch_openml(data_id=OPENML_FREQ_ID, as_frame=True)
    df = dataset.frame

    print(f"  -> {len(df):,} contrats, {df.shape[1]} colonnes")
    df.to_parquet(POLICIES_PARQUET, index=False)
    print(f"  -> ecrit dans {POLICIES_PARQUET}")

    return df


if __name__ == "__main__":
    extract_policies()