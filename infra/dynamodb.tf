resource "aws_dynamodb_table" "articles" {
  name           = var.dynamodb_table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "url"
  range_key      = "at"

  attribute {
    name = "url"
    type = "S"
  }

  attribute {
    name = "at"
    type = "N"
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
}
