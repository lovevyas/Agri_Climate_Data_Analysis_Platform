data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../aws/lambda/trigger_glue.py"
  output_path = "${path.module}/../aws/lambda/trigger_glue.zip"
}

resource "aws_lambda_function" "trigger_glue" {
  function_name    = "${var.project_name}-trigger-glue"
  role             = aws_iam_role.lambda_role.arn
  handler          = "trigger_glue.lambda_handler"
  runtime          = "python3.12"
  timeout          = 10
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      GLUE_JOB_NAME = aws_glue_job.etl.name
      S3_BUCKET_NAME = aws_s3_bucket.data_lake.id
      RDS_HOST       = element(split(":", aws_db_instance.postgres.endpoint), 0)
      RDS_PORT       = "5432"
      RDS_DB         = "agri_climate"
      RDS_USER       = "dbadmin"
      RDS_PASSWORD   = random_password.db_password.result
    }
  }
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_glue.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.data_lake.arn
}

resource "aws_s3_bucket_notification" "csv_upload" {
  bucket = aws_s3_bucket.data_lake.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.trigger_glue.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/"
    filter_suffix       = ".csv"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
