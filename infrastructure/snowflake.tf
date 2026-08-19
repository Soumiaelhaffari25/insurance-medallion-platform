# Structure Snowflake 
# storage integration (lien vers S3) et external stage.

# --- Database + schemas medaillon ---
resource "snowflake_database" "insurance" {
  name = "INSURANCE"
}

resource "snowflake_schema" "raw" {
  database = snowflake_database.insurance.name
  name     = "RAW"
}

resource "snowflake_schema" "staging" {
  database = snowflake_database.insurance.name
  name     = "STAGING"
}

resource "snowflake_schema" "marts" {
  database = snowflake_database.insurance.name
  name     = "MARTS"
}

# --- Warehouse XS avec auto-suspend ---
resource "snowflake_warehouse" "transform" {
  name           = "TRANSFORM_WH"
  warehouse_size = "XSMALL"

  auto_suspend = 60   # Suspension apres 60s d'inactivite.
  auto_resume  = true # Redemarre automatiquement a la demande.

  initially_suspended = true # Ne consomme rien tant qu'on ne l'utilise pas.
}

# --- Role de transformation ---
resource "snowflake_role" "transformer" {
  name = "TRANSFORMER"
}

# --- Storage integration : le pont Snowflake <-> S3 ---
# C'est elle qui renvoie l'ARN et l'External ID a reporter dans iam.tf.
resource "snowflake_storage_integration" "s3" {
  name    = "S3_INTEGRATION"
  type    = "EXTERNAL_STAGE"
  enabled = true

  storage_provider          = "S3"
  storage_aws_role_arn      = aws_iam_role.snowflake.arn
  storage_allowed_locations = ["s3://${var.s3_bucket_name}/raw/"]
}

# --- External stage : pointe vers S3 via l'integration ---
resource "snowflake_stage" "s3_raw" {
  name                = "S3_RAW_STAGE"
  url                 = "s3://${var.s3_bucket_name}/raw/"
  database            = snowflake_database.insurance.name
  schema              = snowflake_schema.raw.name
  storage_integration = snowflake_storage_integration.s3.name
}