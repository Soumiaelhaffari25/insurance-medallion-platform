"""Pipeline cloud observable : execute les transformations Snowflake
et publie logs + metriques dans AWS CloudWatch.

Demontre le monitoring de production : chaque etape est tracee,
et un echec declenche l'alarme CloudWatch 'pipeline-failure'.
"""
import os
import time
from datetime import datetime

import boto3
import snowflake.connector

REGION = "eu-west-3"
LOG_GROUP = "/insurance-medallion/pipeline"
LOG_STREAM = f"run-{datetime.now():%Y%m%d-%H%M%S}"
NAMESPACE = "insurance-medallion/pipeline"
METRIC = "PipelineRunFailed"

logs_client = boto3.client("logs", region_name=REGION)
cw_client = boto3.client("cloudwatch", region_name=REGION)


def ensure_stream():
    """Cree le log stream (le log group existe deja via Terraform)."""
    try:
        logs_client.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
    except logs_client.exceptions.ResourceAlreadyExistsException:
        pass


def log(message: str):
    """Envoie un message dans CloudWatch Logs + affiche en console."""
    print(f"[{datetime.now():%H:%M:%S}] {message}")
    logs_client.put_log_events(
        logGroupName=LOG_GROUP,
        logStreamName=LOG_STREAM,
        logEvents=[{"timestamp": int(time.time() * 1000), "message": message}],
    )


def publish_failure(failed: int):
    """Publie la metrique d'echec (0 = succes, 1 = echec)."""
    cw_client.put_metric_data(
        Namespace=NAMESPACE,
        MetricData=[{"MetricName": METRIC, "Value": failed, "Unit": "Count"}],
    )


def get_snowflake():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        role=os.environ["SNOWFLAKE_ROLE"],
    )


def run_pipeline():
    ensure_stream()
    log("=== Demarrage du pipeline cloud ===")
    try:
        con = get_snowflake()
        cur = con.cursor()

        # Verification des couches (le vrai chargement/transfo est deja fait par SQLMesh)
        cur.execute("SELECT COUNT(*) FROM INSURANCE.RAW.POLICIES")
        n_bronze = cur.fetchone()[0]
        log(f"Couche Bronze : {n_bronze:,} polices verifiees")

        cur.execute("SELECT COUNT(*) FROM INSURANCE.GOLD.FCT_RISK_METRICS")
        n_gold = cur.fetchone()[0]
        log(f"Couche Gold : {n_gold:,} lignes dans fct_risk_metrics")

        # Controle qualite metier
        cur.execute("SELECT COUNT(*) FROM INSURANCE.GOLD.FCT_RISK_METRICS WHERE earned_premium <= 0")
        n_invalid = cur.fetchone()[0]
        if n_invalid > 0:
            raise ValueError(f"{n_invalid} polices avec prime nulle detectees")
        log("Controle qualite : toutes les primes sont positives")

        con.close()
        log("=== Pipeline termine avec SUCCES ===")
        publish_failure(0)  # succes

    except Exception as e:
        log(f"!!! ECHEC du pipeline : {e}")
        publish_failure(1)  # echec -> declenche l'alarme
        raise


if __name__ == "__main__":
    run_pipeline()