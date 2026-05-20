variable "aws_region" {
  description = "AWS region for resources"
  default     = "eu-west-2"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  default     = "dev"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB articles table"
  default     = "c23-mesopelagic-article-db"
  type        = string
}

variable "loader_role_name" {
  description = "Name of the Loader Lambda IAM role"
  default     = "c23-mesopelagic-loader-lambda-role"
  type        = string
}

variable "reader_role_name" {
  description = "Name of the Reader Lambda IAM role"
  default     = "c23-mesopelagic-reader-lambda-role"
  type        = string
}
