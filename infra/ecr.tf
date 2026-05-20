# ECR Repositories
resource "aws_ecr_repository" "repositories" {
  for_each             = var.ecr_repositories
  name                 = each.value.name
  image_tag_mutability = var.ecr_image_tag_mutability

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
}

# ECR Lifecycle Policies
resource "aws_ecr_lifecycle_policy" "repositories" {
  for_each   = aws_ecr_repository.repositories
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images after ${var.ecr_untagged_image_retention_days} days"
        selection = {
          tagStatus     = "untagged"
          countType     = "sinceImagePushed"
          countUnit     = "days"
          countNumber   = var.ecr_untagged_image_retention_days
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Keep last ${var.ecr_image_retention_count} tagged images"
        selection = {
          tagStatus       = "tagged"
          tagPatternList  = ["*"]
          countType       = "imageCountMoreThan"
          countNumber     = var.ecr_image_retention_count
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
