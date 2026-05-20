# Extract Lambda Function
resource "aws_lambda_function" "extract" {
  function_name = "c23-mesopelagic-extract"
  role           = aws_iam_role.lambda_exec_role.arn
  package_type   = "Image"
  image_uri      = "${aws_ecr_repository.repositories["pipeline"].repository_url}:extract"
  timeout        = 60
  memory_size    = 128

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
  role           = aws_iam_role.lambda_exec_role.arn
  package_type   = "Image"
  image_uri      = "${aws_ecr_repository.repositories["pipeline"].repository_url}:enrich"
  timeout        = 60
  memory_size    = 1024

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
  role           = aws_iam_role.lambda_exec_role.arn
  package_type   = "Image"
  image_uri      = "${aws_ecr_repository.repositories["pipeline"].repository_url}:load"
  timeout        = 60
  memory_size    = 128

  image_config {
    command = ["main.handler"]
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
    Stage       = "load"
  }
}
