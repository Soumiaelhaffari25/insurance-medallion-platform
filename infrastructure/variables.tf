# Variables d'entree du projet.

variable "project_name" {
  description = "Nom du projet, utilise pour prefixer les ressources"
  type        = string
  default     = "insurance-medallion"
}

variable "aws_region" {
  description = "Region AWS de deploiement"
  type        = string
  default     = "eu-west-3" # Paris
}

variable "s3_bucket_name" {
  description = "Nom global unique du bucket S3 (landing zone)"
  type        = string
  # Pas de default : un nom de bucket doit etre unique au monde.
  # Fourni via terraform.tfvars en S6.
}

# --- Snowflake (fournis via TF_VAR_snowflake_* en S6) ---

variable "snowflake_account" {
  description = "Identifiant du compte Snowflake (ex: xy12345.eu-west-1)"
  type        = string
  default     = ""
}

variable "snowflake_user" {
  description = "Utilisateur Snowflake"
  type        = string
  default     = ""
}

variable "snowflake_password" {
  description = "Mot de passe Snowflake"
  type        = string
  sensitive   = true
  default     = ""
}