# HTTP API Gateway
resource "aws_apigatewayv2_api" "articles_api" {
  name          = "c23-mesopelagic-articles-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET"]
    allow_headers = ["Content-Type"]
  }

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
}

# Default stage with auto-deploy
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.articles_api.id
  name        = "$default"
  auto_deploy = true

  tags = {
    Environment = var.environment
    Service     = "media-outlet-monitor"
  }
}

# Lambda integration
resource "aws_apigatewayv2_integration" "api_lambda" {
  api_id                 = aws_apigatewayv2_api.articles_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

# Catch-all route — FastAPI handles all routing
resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.articles_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.api_lambda.id}"
}

# Permission for API Gateway to invoke the Lambda
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.articles_api.execution_arn}/*/*"
}
