# Assume Role Policy for Lambda Services
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Lambda Execution Role (shared by all three Lambda functions)
resource "aws_iam_role" "lambda_exec_role" {
  name               = "c23-mesopelagic-lambda-exec-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
}

# Attach AWS-managed policy for CloudWatch Logs
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline policy for DynamoDB and ECR access
data "aws_iam_policy_document" "lambda_exec_policy" {
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem"
    ]
    resources = [aws_dynamodb_table.articles.arn]
  }

  statement {
    actions = [
      "ecr:GetAuthorizationToken"
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer"
    ]
    resources = [
      aws_ecr_repository.repositories["extract"].arn,
      aws_ecr_repository.repositories["enrich"].arn,
      aws_ecr_repository.repositories["load"].arn
    ]
  }

  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject"
    ]
    resources = ["${aws_s3_bucket.articles_bucket.arn}/*"]
  }
}

resource "aws_iam_role_policy" "lambda_exec" {
  name   = "c23-mesopelagic-lambda-exec-policy"
  role   = aws_iam_role.lambda_exec_role.id
  policy = data.aws_iam_policy_document.lambda_exec_policy.json
}

# Loader Lambda Role (Write Access)
resource "aws_iam_role" "loader_lambda_role" {
  name               = var.loader_role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Environment = var.environment
    Service     = var.service_name
  }
}

data "aws_iam_policy_document" "loader_policy" {
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:UpdateItem"
    ]
    resources = [aws_dynamodb_table.articles.arn]
  }

  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role_policy" "loader_policy" {
  name   = "${var.loader_role_name}DynamoDBPolicy"
  role   = aws_iam_role.loader_lambda_role.id
  policy = data.aws_iam_policy_document.loader_policy.json
}

# Reader Lambda Role (Read Access)
resource "aws_iam_role" "reader_lambda_role" {
  name               = var.reader_role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Environment = var.environment
    Service     = var.service_name
  }
}

data "aws_iam_policy_document" "reader_policy" {
  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]
    resources = [aws_dynamodb_table.articles.arn]
  }

  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role_policy" "reader_policy" {
  name   = "${var.reader_role_name}DynamoDBPolicy"
  role   = aws_iam_role.reader_lambda_role.id
  policy = data.aws_iam_policy_document.reader_policy.json
}

# EventBridge Scheduler Execution Role and Policies

# Assume Role Policy for EventBridge Scheduler Service
data "aws_iam_policy_document" "eventbridge_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

# IAM Role for EventBridge to invoke Step Functions
resource "aws_iam_role" "c23_mesopelagic_eventbridge_sfn_role" {
  name               = "c23-mesopelagic-eventbridge-sfn-role"
  assume_role_policy = data.aws_iam_policy_document.eventbridge_assume_role.json

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
}

# Inline policy granting EventBridge permission to invoke Step Functions
resource "aws_iam_role_policy" "c23_mesopelagic_eventbridge_sfn_policy" {
  name   = "c23-mesopelagic-eventbridge-sfn-policy"
  role   = aws_iam_role.c23_mesopelagic_eventbridge_sfn_role.id
  policy = data.aws_iam_policy_document.eventbridge_sfn_policy.json
}

# Policy document for Step Functions execution
data "aws_iam_policy_document" "eventbridge_sfn_policy" {
  statement {
    actions = [
      "states:StartExecution"
    ]
    resources = [
      data.aws_sfn_state_machine.pipeline_orchestrator.arn
    ]
  }
}
