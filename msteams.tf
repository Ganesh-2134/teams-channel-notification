// -----------------
// MODULES
// -----------------

module "msteams_notification" {
  source                     = "../../modules/msteams_notification"
  cloudwatch_event_name      = "pet-master-CloudWatchPipelineEventRule-msteams-notification"
  region                     = "eu-west-1"
  sns_teams_topic_name       = "pet-master-msteams-notification"
  run_time_version           = "python3.8"
  timeout                    = 15
  lambda_function_name       = "pet-pipelines-master-msteams"
  notification_function_name = "pet-pipelines-master-notifier"
  lambda_memory_size         = 512
  secret_name                = "pet.msteams.webhooks"
  description                = "CodePipeline Pipeline Execution State Change"
  lambda_execution_role      = "arn:aws:iam::194316012118:role/customer_pet_sit_default_lambda_role"

}