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
    extract = {
      name = "c23-mesopelagic-extract"
    }
    enrich = {
      name = "c23-mesopelagic-enrich"
    }
    load = {
      name = "c23-mesopelagic-load"
    }
    streamlit_dashboard = {
      name = "c23-mesopelagic-streamlit-dashboard"
    }
    api_collection = {
      name = "c23-mesopelagic-api"
    }
  }
}

variable "articles_bucket_name" {
  description = "Name of the S3 bucket for intermediate pipeline data"
  default     = "c23-mesopelagic-article-bucket"
  type        = string
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

variable "ecr_scan_on_push" {
  description = "Enable vulnerability scanning on push for ECR repositories"
  default     = true
  type        = bool
}

variable "service_name" {
  description = "Service name for resource tags"
  default     = "media-outlet-monitor"
  type        = string
}

variable "ecs_cluster_name" {
  description = "Name of the existing ECS cluster"
  default     = "c23-ecs-cluster"
  type        = string
}

variable "vpc_name" {
  description = "Name of the VPC to deploy dashboard into"
  default     = "c23-VPC"
  type        = string
}

variable "public_subnet_pattern" {
  description = "Name pattern for public subnets"
  default     = "c23-public-subnet-*"
  type        = string
}

variable "dashboard_log_group_path" {
  description = "CloudWatch log group path for dashboard"
  default     = "/ecs/c23-mesopelagic-dashboard"
  type        = string
}

variable "dashboard_log_retention_days" {
  description = "CloudWatch log retention in days for dashboard"
  default     = 7
  type        = number
}

variable "dashboard_container_port" {
  description = "Port exposed by Streamlit dashboard container"
  default     = 8501
  type        = number
}

variable "dashboard_cpu" {
  description = "CPU units for dashboard ECS task (256 = 0.25 vCPU)"
  default     = "256"
  type        = string
}

variable "dashboard_memory" {
  description = "Memory in MB for dashboard ECS task"
  default     = "512"
  type        = string
}

variable "dashboard_desired_count" {
  description = "Desired number of dashboard tasks"
  default     = 1
  type        = number
}

variable "ecs_task_execution_role_name" {
  description = "Name of the ECS task execution role"
  default     = "ecsTaskExecutionRole"
  type        = string
}
