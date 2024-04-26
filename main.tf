# need to be removed while referncing test
provider "aws" {
  region = var.region
}

resource "aws_sns_topic" "PipelineNotificationTopic" {
  name = var.sns_teams_topic_name
}
resource "aws_sns_topic_subscription" "user_updates_lampda_target" {
  topic_arn = aws_sns_topic.PipelineNotificationTopic.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.NotificationFunction.arn
}

# SNS Topic Policy
resource "aws_sns_topic_policy" "PipelineNotificationTopicPolicy" {
  arn    = aws_sns_topic.PipelineNotificationTopic.arn
  policy = <<EOF
{
  "Id": "AllowCloudwatchNotificationEventsToPublish",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "pipeline-msteams-notification-policy",
      "Effect": "Allow",
      "Principal": {
        "Service": "events.amazonaws.com"
      },
      "Action": [
        "sns:Publish"
      ],
      "Resource": "${aws_sns_topic.PipelineNotificationTopic.arn}"
    }
  ]
}
EOF
}

#creating Cloudwatch event rule creation
resource "aws_cloudwatch_event_rule" "CloudWatchPipelineEventRule" {
  name        = var.cloudwatch_event_name
  description = var.description

  event_pattern = <<EOF
{
  "source": ["aws.codepipeline", "aws.codebuild"],
  "detail-type": ["CodePipeline Pipeline Execution State Change", "CodeBuild Build State Change"]
}
EOF
}

# CloudWatch Events Target
resource "aws_cloudwatch_event_target" "CloudWatchPipelineEventTarget" {
  rule      = aws_cloudwatch_event_rule.CloudWatchPipelineEventRule.name
  arn       = aws_sns_topic.PipelineNotificationTopic.arn
  target_id = var.cloudwatch_event_name
}

resource "aws_lambda_function" "MSTeamsSendFunction" {
  function_name    = var.lambda_function_name
  runtime          = var.run_time_version
  timeout          = var.timeout
  memory_size      = var.lambda_memory_size
  handler          = "msteams_lambda_function.handler"
  role             = var.lambda_execution_role
  filename         = "${path.module}/msteams_lambda_function.zip"
  
  source_code_hash = filebase64("${path.module}/msteams_lambda_function.zip")
}
#   environment {
#     variables = {
#       SECRET_NAME  = var.secret_name,
#       REGION_NAME  = var.region,
#       MSTEAMS_HOST = "directlinegroup.webhook.office.com",
#     }
#   }
# }

#Lambda Permission for SNS to invoke MSTeamsSendFunction
resource "aws_lambda_permission" "MSTeamsLambdaFunctionInvokePermission" {
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.MSTeamsSendFunction.function_name
  principal     = "sns.amazonaws.com"
}

# Lambda Function: NotificationFunction
resource "aws_lambda_function" "NotificationFunction" {
  function_name    = var.notification_function_name
  runtime          = var.run_time_version
  timeout          = var.timeout
  memory_size      = var.lambda_memory_size
  handler          = "notifier_lambda_function.handler"
  role             = var.lambda_execution_role
  filename         = "${path.module}/notifier_lambda_function.zip"
  source_code_hash = filebase64("${path.module}/notifier_lambda_function.zip")

  environment {
    variables = {
      MSTeamsSendFunction = aws_lambda_function.MSTeamsSendFunction.arn
    }
  }
}


# Lambda Permission for SNS to invoke NotificationFunction
resource "aws_lambda_permission" "NotificationFunctionInvokePermission" {
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.NotificationFunction.function_name
  principal     = "sns.amazonaws.com"
}
