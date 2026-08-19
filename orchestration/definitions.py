"""Point d'entree Dagster : rassemble les assets, le job et le schedule.
"""
from dagster import Definitions, define_asset_job, ScheduleDefinition

from orchestration.assets import (
    ingest_raw_data,
    sqlmesh_transform,
    data_quality,
    pipeline_summary,
)

# Job qui materialise tous les assets dans l'ordre des dependances.
pipeline_job = define_asset_job(name="medallion_pipeline")

# Schedule : rafraichissement quotidien a 6h du matin .
daily_schedule = ScheduleDefinition(
    job=pipeline_job,
    cron_schedule="0 6 * * *",
    name="daily_refresh",
)

defs = Definitions(
    assets=[
        ingest_raw_data,
        sqlmesh_transform,
        data_quality,
        pipeline_summary,
    ],
    jobs=[pipeline_job],
    schedules=[daily_schedule],
)