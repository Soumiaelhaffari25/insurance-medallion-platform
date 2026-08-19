# Bucket S3 : landing zone des donnees brutes (Bronze).

resource "aws_s3_bucket" "landing" {
  bucket = var.s3_bucket_name
}

# Versioning : conserve l'historique des objets (tracabilite).
resource "aws_s3_bucket_versioning" "landing" {
  bucket = aws_s3_bucket.landing.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Chiffrement au repos (SSE-S3, gratuit).
resource "aws_s3_bucket_server_side_encryption_configuration" "landing" {
  bucket = aws_s3_bucket.landing.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Blocage total de l'acces public : rien n'est expose sur Internet.
resource "aws_s3_bucket_public_access_block" "landing" {
  bucket = aws_s3_bucket.landing.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}