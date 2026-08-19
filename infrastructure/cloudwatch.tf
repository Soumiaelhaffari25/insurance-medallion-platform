# Monitoring du pipeline : log group + alarme sur echec de run.

# Log group : recueille les logs d'execution du pipeline Dagster.
resource "aws_cloudwatch_log_group" "pipeline" {
  name              = "/${var.project_name}/pipeline"
  retention_in_days = 7
}

# Metrique custom + alarme : declenchee si le pipeline signale un echec.
# Le pipeline Dagster publiera une metrique "PipelineRunFailed".
resource "aws_cloudwatch_metric_alarm" "pipeline_failure" {
  alarm_name          = "${var.project_name}-pipeline-failure"
  alarm_description   = "Se declenche quand un run du pipeline echoue."
  namespace           = "${var.project_name}/pipeline"
  metric_name         = "PipelineRunFailed"
  statistic           = "Sum"
  period              = 300 # 5 minutes
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
}