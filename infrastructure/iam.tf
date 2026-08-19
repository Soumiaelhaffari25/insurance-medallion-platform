# Role IAM assumable par Snowflake pour lire le bucket S3.

# Valeurs renvoyees par la storage integration Snowflake .
variable "snowflake_iam_user_arn" {
  description = "ARN de l'utilisateur IAM de Snowflake (STORAGE_AWS_IAM_USER_ARN)"
  type        = string
  default     = "arn:aws:iam::094374929950:root" # placeholder temporaire
}

variable "snowflake_external_id" {
  description = "External ID renvoye par Snowflake (STORAGE_AWS_EXTERNAL_ID)"
  type        = string
  default     = "PLACEHOLDER_EXTERNAL_ID"
}

# Policy de confiance : qui peut assumer ce role.
data "aws_iam_policy_document" "snowflake_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [var.snowflake_iam_user_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "sts:ExternalId"
      values   = [var.snowflake_external_id]
    }
  }
}

resource "aws_iam_role" "snowflake" {
  name               = "${var.project_name}-snowflake-role"
  assume_role_policy = data.aws_iam_policy_document.snowflake_assume.json
}

# Policy de lecture du bucket S3.
data "aws_iam_policy_document" "s3_read" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion"
    ]
    resources = ["${aws_s3_bucket.landing.arn}/*"]
  }

  statement {
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.landing.arn]
  }
}

resource "aws_iam_role_policy" "snowflake_s3_read" {
  name   = "${var.project_name}-s3-read"
  role   = aws_iam_role.snowflake.id
  policy = data.aws_iam_policy_document.s3_read.json
}