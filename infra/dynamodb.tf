resource "aws_dynamodb_table" "articles" {
  name           = var.dynamodb_table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "target_name"
  range_key      = "article_id"

  attribute {
    name = "target_name"
    type = "S"
  }
  attribute {
    name = "article_id"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Service     = var.service_name
  }
}
