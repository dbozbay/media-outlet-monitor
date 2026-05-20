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

# ECR Repository Outputs
output "pipeline_repository_url" {
  value       = aws_ecr_repository.repositories["pipeline"].repository_url
  description = "URL of the c23-mesopelagic-pipeline ECR repository for push/pull operations"
}

output "streamlit_dashboard_repository_url" {
  value       = aws_ecr_repository.repositories["streamlit_dashboard"].repository_url
  description = "URL of the c23-mesopelagic-streamlit-dashboard ECR repository for push/pull operations"
}

output "api_collection_repository_url" {
  value       = aws_ecr_repository.repositories["api_collection"].repository_url
  description = "URL of the c23-mesopelagic-api-collection ECR repository for push/pull operations"
}
