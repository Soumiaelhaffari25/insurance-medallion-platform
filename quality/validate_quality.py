from pathlib import Path

import duckdb
import great_expectations as gx
from great_expectations.dataset import PandasDataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "transform" / "insurance.db"


def valider_silver():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df_pol = con.execute("SELECT * FROM silver.stg_policies").fetchdf()
    df_clm = con.execute("SELECT * FROM silver.stg_claims").fetchdf()
    con.close()

    print(f"Great Expectations version : {gx.__version__}")
    print(f"Silver policies : {len(df_pol):,} lignes")
    print(f"Silver claims   : {len(df_clm):,} lignes\n")

    ds_pol = PandasDataset(df_pol)
    ds_clm = PandasDataset(df_clm)

    resultats = []

    def check(nom, res):
        ok = res["success"]
        print(f"  [{'OK   ' if ok else 'ECHEC'}] {nom}")
        resultats.append(ok)

    print("=== POLICIES ===")
    check("id_pol non null",
          ds_pol.expect_column_values_to_not_be_null("id_pol"))
    check("id_pol unique",
          ds_pol.expect_column_values_to_be_unique("id_pol"))
    check("exposure dans ]0,1]",
          ds_pol.expect_column_values_to_be_between(
              "exposure", min_value=0, max_value=1, strict_min=True))
    check("driver_age dans [18,99]",
          ds_pol.expect_column_values_to_be_between(
              "driver_age", min_value=18, max_value=99))
    check("veh_gas dans {Regular, Diesel}",
          ds_pol.expect_column_values_to_be_in_set(
              "veh_gas", ["Regular", "Diesel"]))
    check("bonus_malus dans [50,350]",
          ds_pol.expect_column_values_to_be_between(
              "bonus_malus", min_value=50, max_value=350))

    print("\n=== CLAIMS ===")
    check("id_pol non null",
          ds_clm.expect_column_values_to_not_be_null("id_pol"))
    check("claim_amount dans ]0,100000]",
          ds_clm.expect_column_values_to_be_between(
              "claim_amount", min_value=0, max_value=100000, strict_min=True))

    suite_pol = ds_pol.get_expectation_suite(discard_failed_expectations=False)
    suite_path = PROJECT_ROOT / "quality" / "expectations" / "policies_suite.json"
    suite_path.parent.mkdir(parents=True, exist_ok=True)
    import json
    with open(suite_path, "w", encoding="utf-8") as f:
        json.dump(suite_pol.to_json_dict(), f, indent=2)
    print(f"\nSuite d'attentes sauvegardee : {suite_path.name}")

    total, reussis = len(resultats), sum(resultats)
    print(f"\n{'='*45}")
    print(f"BILAN : {reussis}/{total} attentes GE reussies")
    print(f"{'='*45}")

    if reussis < total:
        raise SystemExit("Des attentes GE ont echoue.")
    print("Toutes les attentes GE sont passees.")


def valider_gold():
    """Validation qualite de la couche Gold (coherence metier)."""
    from great_expectations.dataset import PandasDataset

    con = duckdb.connect(str(DB_PATH), read_only=True)
    df_metrics = con.execute("""
        SELECT id_pol, exposure, claim_count, claim_amount,
               earned_premium, loss_ratio, frequency, severity
        FROM gold.fct_risk_metrics
    """).fetchdf()
    df_region = con.execute("SELECT * FROM gold.dim_region").fetchdf()
    con.close()

    print(f"\nGold fct_risk_metrics : {len(df_metrics):,} lignes")
    print(f"Gold dim_region       : {len(df_region):,} lignes\n")

    ds_metrics = PandasDataset(df_metrics)
    ds_region = PandasDataset(df_region)

    resultats = []

    def check(nom, res):
        ok = res["success"]
        print(f"  [{'OK   ' if ok else 'ECHEC'}] {nom}")
        resultats.append(ok)

    # ---- FCT_RISK_METRICS : coherence metier ----
    print("=== GOLD : fct_risk_metrics ===")
    check("id_pol non null",
          ds_metrics.expect_column_values_to_not_be_null("id_pol"))
    check("id_pol unique",
          ds_metrics.expect_column_values_to_be_unique("id_pol"))
    check("loss_ratio >= 0 (jamais negatif)",
          ds_metrics.expect_column_values_to_be_between(
              "loss_ratio", min_value=0, max_value=None))
    check("claim_count >= 0",
          ds_metrics.expect_column_values_to_be_between(
              "claim_count", min_value=0, max_value=None))
    check("claim_amount >= 0",
          ds_metrics.expect_column_values_to_be_between(
              "claim_amount", min_value=0, max_value=None))
    check("earned_premium > 0 (toute police a une prime)",
          ds_metrics.expect_column_values_to_be_between(
              "earned_premium", min_value=0, max_value=None, strict_min=True))

    # ---- DIM_REGION : integrite dimension ----
    print("\n=== GOLD : dim_region ===")
    check("region_key unique (cle de substitution)",
          ds_region.expect_column_values_to_be_unique("region_key"))
    check("region_key non null",
          ds_region.expect_column_values_to_not_be_null("region_key"))

    total, reussis = len(resultats), sum(resultats)
    print(f"\n{'='*45}")
    print(f"BILAN GOLD : {reussis}/{total} attentes GE reussies")
    print(f"{'='*45}")

    if reussis < total:
        raise SystemExit("Des attentes GE Gold ont echoue.")
    print("Toutes les attentes GE Gold sont passees.")

if __name__ == "__main__":
    valider_silver()
    valider_gold()