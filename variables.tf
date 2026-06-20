variable "aws_region" {
  default = "eu-central-1"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for storing transformed CSV files"
  type        = string
  default = "alpenmechanik-datalake"
}

variable "sheet_key" {
  description = "Google Sheet ID"
  type        = string
}

variable "ssm_path" {
  description = "SSM Parameter path containing credentials"
  type        = string
}

variable "lambda_version" {
  description = "Git SHA of the ETL repo build to deploy"
  type        = string
  default = "latest"
}