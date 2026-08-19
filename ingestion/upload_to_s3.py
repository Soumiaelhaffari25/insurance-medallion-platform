import os
from datetime import date

import boto3

from config import CLAIMS_PARQUET, POLICIES_PARQUET

# Partition par date de chargement (chargements incrementaux facilites)
LOAD_DATE = date.today().isoformat()


def upload_to_s3():
    bucket = os.environ["S3_BUCKET_NAME"]
    s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "eu-west-3"))

    uploads = [
        (POLICIES_PARQUET, f"raw/policies/load_date={LOAD_DATE}/policies.parquet"),
        (CLAIMS_PARQUET, f"raw/claims/load_date={LOAD_DATE}/claims.parquet"),
    ]

    for local_path, s3_key in uploads:
        print(f"Upload {local_path.name} -> s3://{bucket}/{s3_key}")
        s3.upload_file(str(local_path), bucket, s3_key)

    print("Upload termine.")


if __name__ == "__main__":
    upload_to_s3()