# S3 bucket for intermediate pipeline data (extract → enrich)
resource "aws_s3_bucket" "articles_bucket" {
  bucket = var.articles_bucket_name

  force_destroy = true

  tags = {
    Environment = var.environment
    Service     = var.service_name
  }
}

resource "aws_s3_bucket_public_access_block" "articles_bucket" {
  bucket = aws_s3_bucket.articles_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "articles_bucket" {
  bucket = aws_s3_bucket.articles_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "articles_bucket" {
  bucket = aws_s3_bucket.articles_bucket.id

  rule {
    id     = "expire-articles-data"
    status = "Enabled"

    filter {}

    expiration {
      days = 1
    }
  }
}
