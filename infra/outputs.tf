output "bucket_name" {
  description = "Name of the S3 bucket holding raw/curated data and scripts"
  value       = aws_s3_bucket.data_lake.id
}

output "glue_role_arn" {
  description = "IAM role ARN Glue will assume to run the ETL job"
  value       = aws_iam_role.glue_role.arn
}

output "lambda_role_arn" {
  description = "IAM role ARN Lambda will assume to trigger the Glue job"
  value       = aws_iam_role.lambda_role.arn
}

output "db_endpoint" {
  description = "RDS Postgres connection endpoint (host:port)"
  value       = aws_db_instance.postgres.endpoint
}

output "db_password" {
  description = "Generated master password for the RDS instance"
  value       = random_password.db_password.result
  sensitive   = true
}

output "glue_job_name" {
  description = "Name of the Glue ETL job"
  value       = aws_glue_job.etl.name
}

output "lambda_function_name" {
  description = "Name of the Lambda function that triggers the Glue job"
  value       = aws_lambda_function.trigger_glue.function_name
}
