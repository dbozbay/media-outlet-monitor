# Extract Lambda Function
resource "aws_lambda_function" "extract" {
  function_name = "c23-mesopelagic-extract"
  role          = aws_iam_role.lambda_exec_role.arn
  package_type  = "Image"
  image_uri     = format("%s:latest", aws_ecr_repository.repositories["extract"].repository_url)
  timeout       = 60
  memory_size   = 128

  image_config {
    command = ["main.handler"]
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
    Stage       = "extract"
  }
}

# Enrich Lambda Function
resource "aws_lambda_function" "enrich" {
  function_name = "c23-mesopelagic-enrich"
  role          = aws_iam_role.lambda_exec_role.arn
  package_type  = "Image"
  image_uri     = format("%s:latest", aws_ecr_repository.repositories["enrich"].repository_url)
  timeout       = 60
  memory_size   = 1024

  image_config {
    command = ["main.handler"]
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
    Stage       = "enrich"
  }
}

# Upload Lambda Function
resource "aws_lambda_function" "upload" {
  function_name = "c23-mesopelagic-upload"
  role          = aws_iam_role.lambda_exec_role.arn
  package_type  = "Image"
  image_uri     = format("%s:latest", aws_ecr_repository.repositories["load"].repository_url)
  timeout       = 60
  memory_size   = 128

  image_config {
    command = ["main.handler"]
  }

  environment {
    variables = {
      DYNAMO_TABLE_NAME = var.dynamodb_table_name
      AWS_REGION_NAME   = var.aws_region
    }
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
    Stage       = "load"
  }
}

# API Lambda Function
resource "aws_lambda_function" "api" {
  function_name = "c23-mesopelagic-api"
  role          = aws_iam_role.reader_lambda_role.arn
  package_type  = "Image"
  image_uri     = format("%s:latest", aws_ecr_repository.repositories["api_collection"].repository_url)
  timeout       = 30
  memory_size   = 128

  image_config {
    command = ["main.handler"]
  }

  environment {
    variables = {
      DYNAMO_TABLE_NAME = var.dynamodb_table_name
      AWS_REGION_NAME   = var.aws_region
    }
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
    Stage       = "api"
  }
}
