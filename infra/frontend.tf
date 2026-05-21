# Data source for current AWS account ID
data "aws_caller_identity" "current" {}

# Data source for existing ECS cluster
data "aws_ecs_cluster" "main" {
  cluster_name = var.ecs_cluster_name
}

# Data source for existing VPC
data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = [var.vpc_name]
  }
}

# Data source for public subnets in the VPC
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }

  filter {
    name   = "tag:Name"
    values = [var.public_subnet_pattern]
  }
}

# CloudWatch Log Group for Streamlit dashboard
resource "aws_cloudwatch_log_group" "dashboard" {
  name              = var.dashboard_log_group_path
  retention_in_days = var.dashboard_log_retention_days

  tags = {
    Environment = var.environment
    Service     = var.service_name
  }
}

# IAM Role for ECS Task (runtime permissions)
data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "dashboard_task_role" {
  name               = "c23-mesopelagic-dashboard-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = {
    Environment = var.environment
    Service     = var.service_name
  }
}

data "aws_iam_policy_document" "dashboard_task_policy" {
  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]
    resources = [aws_dynamodb_table.articles.arn]
  }
}

resource "aws_iam_role_policy" "dashboard_task_policy" {
  name   = "c23-mesopelagic-dashboard-dynamodb-read"
  role   = aws_iam_role.dashboard_task_role.id
  policy = data.aws_iam_policy_document.dashboard_task_policy.json
}

# ECS Task Definition
resource "aws_ecs_task_definition" "dashboard" {
  family                   = "c23-mesopelagic-dashboard-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.dashboard_cpu
  memory                   = var.dashboard_memory
  execution_role_arn       = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.ecs_task_execution_role_name}"
  task_role_arn            = aws_iam_role.dashboard_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "c23-mesopelagic-dashboard"
      image     = "${aws_ecr_repository.repositories["streamlit_dashboard"].repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = var.dashboard_container_port
          hostPort      = var.dashboard_container_port
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "DYNAMO_TABLE_NAME"
          value = var.dynamodb_table_name
        },
        {
          name  = "AWS_REGION_NAME"
          value = var.aws_region
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.dashboard.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Environment = var.environment
    Service     = var.service_name
  }
}

# Security Group for Streamlit dashboard
resource "aws_security_group" "dashboard" {
  name        = "c23-mesopelagic-dashboard-sg"
  description = "Security group for Streamlit dashboard ECS service"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    description = "Allow Streamlit port from anywhere"
    from_port   = var.dashboard_container_port
    to_port     = var.dashboard_container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment
    Service     = var.service_name
  }
}

# ECS Service
resource "aws_ecs_service" "dashboard" {
  name            = "c23-mesopelagic-dashboard-service"
  cluster         = data.aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.dashboard.arn
  desired_count   = var.dashboard_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.public.ids
    security_groups  = [aws_security_group.dashboard.id]
    assign_public_ip = true
  }

  tags = {
    Environment = var.environment
    Service     = var.service_name
  }

  depends_on = [
    aws_cloudwatch_log_group.dashboard,
    aws_ecs_task_definition.dashboard,
    aws_security_group.dashboard
  ]
}

# Outputs
output "dashboard_service_name" {
  value       = aws_ecs_service.dashboard.name
  description = "Name of the Streamlit dashboard ECS service"
}

output "dashboard_log_group" {
  value       = aws_cloudwatch_log_group.dashboard.name
  description = "CloudWatch log group for dashboard logs"
}

output "dashboard_security_group_id" {
  value       = aws_security_group.dashboard.id
  description = "Security group ID for the dashboard service"
}
