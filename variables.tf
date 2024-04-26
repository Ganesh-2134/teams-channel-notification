
variable "sns_teams_topic_name" {
  description = "The topic name"
  type        = string
}
variable "cloudwatch_event_name" {
  description = "the Cloudwatch Event name"
  type        = string
}
variable "run_time_version" {
  description = "the python run time"
  type        = string
}
variable "timeout" {
  description = "Timeout for the CloudWatch Events target in seconds"
  type        = number
}

variable "lambda_function_name" {
  description = "lambda functione name for the ms teams"
  type        = string
}
variable "notification_function_name" {
  description = "lambda functione name for the ms teams"
  type        = string
}


variable "lambda_memory_size" {
  description = "Memory size for the Lambda function"
  type        = number
}
variable "secret_name" {
  description = "Name for the secret"
  type        = string
}
variable "region" {
  description = "Enter the region"
  type        = string
}
variable "description" {
  description = "Enter the description for the event"
  type        = string
}

variable "lambda_execution_role" {
  description = "Provide the Lambda execution role ARN"
  type        = string
}

