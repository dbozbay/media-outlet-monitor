output "dynamodb_table_name" {
  value       = aws_dynamodb_table.articles.name
  description = "Name of the DynamoDB table"
}

output "dynamodb_table_arn" {
  value       = aws_dynamodb_table.articles.arn
  description = "ARN of the DynamoDB table"
}

output "loader_lambda_role_arn" {
  value       = aws_iam_role.loader_lambda_role.arn
  description = "ARN of the Loader Lambda execution role"
}

output "reader_lambda_role_arn" {
  value       = aws_iam_role.reader_lambda_role.arn
  description = "ARN of the Reader Lambda execution role (shared by dashboard and social media lambdas)"
}
