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

variable "ecr_repositories" {
  description = "Map of ECR repositories to create"
  type = map(object({
    name = string
  }))
  default = {
    pipeline = {
      name = "c23-mesopelagic-pipeline"
    }
    streamlit_dashboard = {
      name = "c23-mesopelagic-streamlit-dashboard"
    }
    api_collection = {
      name = "c23-mesopelagic-api-collection"
    }
  }
}

variable "ecr_image_tag_mutability" {
  description = "Image tag mutability setting for ECR repositories"
  default     = "MUTABLE"
  type        = string
}

variable "ecr_image_retention_count" {
  description = "Number of tagged images to retain in each ECR repository"
  default     = 5
  type        = number
}

variable "ecr_untagged_image_retention_days" {
  description = "Number of days to retain untagged images in ECR repositories"
  default     = 7
  type        = number
}
