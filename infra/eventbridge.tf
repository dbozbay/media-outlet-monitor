# Data source to fetch the existing Step Functions state machine
data "aws_sfn_state_machine" "pipeline_orchestrator" {
  name = "c23-mesopelagic-state-machine"
}

# EventBridge Scheduler for Step Functions pipeline
resource "aws_scheduler_schedule" "c23_mesopelagic_pipeline_scheduler" {
  name                = "c23-mesopelagic-pipeline-scheduler"
  description         = "Triggers Step Functions ingestion pipeline every 5 minutes"
  schedule_expression = "rate(5 minutes)"
  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = data.aws_sfn_state_machine.pipeline_orchestrator.arn
    role_arn = aws_iam_role.c23_mesopelagic_eventbridge_sfn_role.arn
  }
}
