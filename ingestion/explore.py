import pandas as pd

from config import CLAIMS_PARQUET, POLICIES_PARQUET

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)


def explore(name, path):
    print("=" * 70)
    print(f"  {name}  ({path.name})")
    print("=" * 70)
    df = pd.read_parquet(path)

    print(f"\nDimensions : {df.shape[0]:,} lignes x {df.shape[1]} colonnes\n")
    print("Colonnes & types :")
    print(df.dtypes)
    print("\n5 premieres lignes :")
    print(df.head())
    print("\nStatistiques (numeriques) :")
    print(df.describe())
    print()


if __name__ == "__main__":
    explore("POLICIES (freq)", POLICIES_PARQUET)
    explore("CLAIMS (sev)", CLAIMS_PARQUET)