# ECR Repository: Pipeline
resource "aws_ecr_repository" "pipeline" {
  name                 = "c23-mesopelagic-pipeline"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
}

# ECR Repository: Streamlit Dashboard
resource "aws_ecr_repository" "streamlit_dashboard" {
  name                 = "c23-mesopelagic-streamlit-dashboard"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
}

# ECR Repository: API Collection
resource "aws_ecr_repository" "api_collection" {
  name                 = "c23-mesopelagic-api-collection"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
}

# Lifecycle Policy for Pipeline Repository
resource "aws_ecr_lifecycle_policy" "pipeline_policy" {
  repository = aws_ecr_repository.pipeline.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 3 tagged images"
        selection = {
          tagStatus       = "tagged"
          tagPatternList  = ["*"]
          countType       = "imageCountMoreThan"
          countNumber     = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Lifecycle Policy for Streamlit Dashboard Repository
resource "aws_ecr_lifecycle_policy" "streamlit_dashboard_policy" {
  repository = aws_ecr_repository.streamlit_dashboard.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 3 tagged images"
        selection = {
          tagStatus       = "tagged"
          tagPatternList  = ["*"]
          countType       = "imageCountMoreThan"
          countNumber     = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Lifecycle Policy for API Collection Repository
resource "aws_ecr_lifecycle_policy" "api_collection_policy" {
  repository = aws_ecr_repository.api_collection.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 3 tagged images"
        selection = {
          tagStatus       = "tagged"
          tagPatternList  = ["*"]
          countType       = "imageCountMoreThan"
          countNumber     = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Outputs
output "pipeline_repository_url" {
  value       = aws_ecr_repository.pipeline.repository_url
  description = "URL of the c23-mesopelagic-pipeline ECR repository for push/pull operations"
}

output "streamlit_dashboard_repository_url" {
  value       = aws_ecr_repository.streamlit_dashboard.repository_url
  description = "URL of the c23-mesopelagic-streamlit-dashboard ECR repository for push/pull operations"
}

output "api_collection_repository_url" {
  value       = aws_ecr_repository.api_collection.repository_url
  description = "URL of the c23-mesopelagic-api-collection ECR repository for push/pull operations"
}
