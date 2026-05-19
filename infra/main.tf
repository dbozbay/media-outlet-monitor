terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "eu-west-2"
  type    = string
}

variable "environment" {
  default = "dev"
  type    = string
}

# DynamoDB Table
resource "aws_dynamodb_table" "articles" {
  name           = "c23-mesopelagic-article-db"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "url"
  range_key      = "at"

  attribute {
    name = "url"
    type = "S"
  }

  attribute {
    name = "at"
    type = "N"
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
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
  name               = "LoaderLambdaRole"
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
}

resource "aws_iam_role_policy" "loader_policy" {
  name   = "LoaderDynamoDBPolicy"
  role   = aws_iam_role.loader_lambda_role.id
  policy = data.aws_iam_policy_document.loader_policy.json
}

# Reader Lambda Role (Read Access) - Shared by Dashboard and Social Media Integration
resource "aws_iam_role" "reader_lambda_role" {
  name               = "ReaderLambdaRole"
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
}

resource "aws_iam_role_policy" "reader_policy" {
  name   = "ReaderDynamoDBPolicy"
  role   = aws_iam_role.reader_lambda_role.id
  policy = data.aws_iam_policy_document.reader_policy.json
}

# Outputs
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