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

# Inline policy for DynamoDB access
data "aws_iam_policy_document" "lambda_dynamodb_policy" {
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem"
    ]
    resources = [aws_dynamodb_table.articles.arn]
  }
}

resource "aws_iam_role_policy" "lambda_dynamodb" {
  name   = "c23-mesopelagic-lambda-dynamodb-policy"
  role   = aws_iam_role.lambda_exec_role.id
  policy = data.aws_iam_policy_document.lambda_dynamodb_policy.json
}
# Assume Role Policy for Lambdas
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Loader Lambda Role (Write Access)
resource "aws_iam_role" "loader_lambda_role" {
  name               = var.loader_role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
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

# Reader Lambda Role (Read Access) - Shared by Dashboard and Social Media Integration
resource "aws_iam_role" "reader_lambda_role" {
  name               = var.reader_role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
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
