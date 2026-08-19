# Insurance Medallion Platform - Infrastructure as Code
#
# Ressources reparties par fichier :
#   s3.tf         -> bucket landing zone
#   iam.tf        -> role assumable par Snowflake
#   cloudwatch.tf -> monitoring du pipeline
#   snowflake.tf  -> database, schemas, warehouse, integration, stage
#
# Variables sensibles : via TF_VAR_* (env). Voir terraform.tfvars.example.