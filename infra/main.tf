resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "raw_csvs" {
  for_each = fileset("${path.module}/../datasets/raw", "*.csv")

  bucket = aws_s3_bucket.data_lake.id
  key    = "raw/${each.value}"
  source = "${path.module}/../datasets/raw/${each.value}"
  etag   = filemd5("${path.module}/../datasets/raw/${each.value}")
}

resource "aws_s3_object" "glue_script" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "scripts/glue_job.py"
  source = "${path.module}/../aws/glue/glue_job.py"
  etag   = filemd5("${path.module}/../aws/glue/glue_job.py")
}

# Glue runs a single entry-point script, so the modules glue_job.py imports
# have to travel separately as a zip referenced by --extra-py-files.
locals {
  glue_modules = ["glue_schemas.py", "glue_transforms.py", "glue_load.py", "glue_analytics.py"]
}

data "archive_file" "glue_modules" {
  type        = "zip"
  output_path = "${path.module}/../aws/glue/glue_modules.zip"

  dynamic "source" {
    for_each = local.glue_modules
    content {
      content  = file("${path.module}/../aws/glue/${source.value}")
      filename = source.value
    }
  }
}

resource "aws_s3_object" "glue_modules" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "scripts/glue_modules.zip"
  source = data.archive_file.glue_modules.output_path
  etag   = data.archive_file.glue_modules.output_md5
}
