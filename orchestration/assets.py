"""Assets Dagster : orchestration du pipeline medaillon.
"""
import subprocess
import sys
from pathlib import Path

from dagster import asset, AssetExecutionContext, MaterializeResult, MetadataValue

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRANSFORM_DIR = PROJECT_ROOT / "transform"
QUALITY_DIR = PROJECT_ROOT / "quality"

# Python exact du venv qui execute Dagster : garantit l'acces aux libs.
PYTHON = sys.executable

SQLMESH = str(Path(sys.executable).parent / "sqlmesh.exe")

def _run(context, cmd, cwd):
    """Execute une commande et remonte stdout/stderr dans les logs Dagster."""
    context.log.info(f"Execution : {' '.join(cmd)} (cwd={cwd})")
    result = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True
    )
    if result.stdout:
        context.log.info(result.stdout)
    if result.stderr:
        context.log.warning(result.stderr)
    if result.returncode != 0:
        raise Exception(
            f"Echec (code {result.returncode}) : {' '.join(cmd)}\n{result.stderr}"
        )
    return result.stdout


@asset
def ingest_raw_data(context: AssetExecutionContext) -> MaterializeResult:
    """Charge les Parquet freMTPL2 dans DuckDB (couche Bronze)."""
    out = _run(context, [PYTHON, "seed_duckdb.py"], TRANSFORM_DIR)
    return MaterializeResult(
        metadata={"etape": "Bronze", "log": MetadataValue.text(out[-500:])}
    )


@asset(deps=[ingest_raw_data])
def sqlmesh_transform(context: AssetExecutionContext) -> MaterializeResult:
    """Lance SQLMesh : transformations Silver + Gold sur DuckDB."""
    out = _run(
        context,
        [SQLMESH, "plan", "--no-prompts", "--auto-apply"],
        TRANSFORM_DIR,
    )
    return MaterializeResult(
        metadata={"etape": "Silver + Gold", "log": MetadataValue.text(out[-500:])}
    )


@asset(deps=[sqlmesh_transform])
def data_quality(context: AssetExecutionContext) -> MaterializeResult:
    """Validation Great Expectations sur la couche Silver."""
    out = _run(context, [PYTHON, "validate_quality.py"], QUALITY_DIR)
    return MaterializeResult(
        metadata={"etape": "Qualite GE", "log": MetadataValue.text(out[-500:])}
    )


@asset(deps=[data_quality])
def pipeline_summary(context: AssetExecutionContext) -> MaterializeResult:
    """Recapitulatif final du pipeline."""
    context.log.info("Pipeline complet execute avec succes.")
    return MaterializeResult(
        metadata={
            "statut": "OK",
            "couches": "Bronze -> Silver -> Gold -> Qualite",
        }
    )