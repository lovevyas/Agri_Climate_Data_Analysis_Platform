resource "aws_glue_job" "etl" {
  name     = local.glue_job_name
  role_arn = aws_iam_role.glue_role.arn

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 15
  max_retries       = 0 

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.data_lake.id}/${aws_s3_object.glue_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--TempDir"                          = "s3://${aws_s3_bucket.data_lake.id}/temp/"
    "--job-bookmark-option"              = "job-bookmark-disable"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"                   = "true"
    "--extra-py-files"                   = "s3://${aws_s3_bucket.data_lake.id}/${aws_s3_object.glue_modules.key}"
    "--additional-python-modules"        = "psycopg2-binary"
  }
}
