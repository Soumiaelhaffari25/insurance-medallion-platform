# Sorties affichees apres terraform apply.

output "s3_bucket_name" {
  description = "Nom du bucket S3 landing zone"
  value       = aws_s3_bucket.landing.id
}

output "s3_bucket_arn" {
  description = "ARN du bucket S3"
  value       = aws_s3_bucket.landing.arn
}

output "snowflake_role_arn" {
  description = "ARN du role IAM assumable par Snowflake"
  value       = aws_iam_role.snowflake.arn
}

output "cloudwatch_log_group" {
  description = "Nom du log group du pipeline"
  value       = aws_cloudwatch_log_group.pipeline.name
}

# Valeurs a reporter dans iam.tf apres creation .
output "storage_integration_note" {
  description = "Rappel : recuperer ARN + External ID via DESC INTEGRATION"
  value       = " lancer DESC INTEGRATION S3_INTEGRATION dans Snowflake, puis reporter STORAGE_AWS_IAM_USER_ARN et STORAGE_AWS_EXTERNAL_ID dans terraform.tfvars."
}