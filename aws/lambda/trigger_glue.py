import json
import boto3
import os

glue = boto3.client("glue")

GLUE_JOB_NAME = os.environ["GLUE_JOB_NAME"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
RDS_HOST = os.environ["RDS_HOST"]
RDS_PORT = os.environ["RDS_PORT"]
RDS_DB = os.environ["RDS_DB"]
RDS_USER = os.environ["RDS_USER"]
RDS_PASSWORD = os.environ["RDS_PASSWORD"]

def lambda_handler(event, context):
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    print(f"S3 event: s3://{bucket}/{key}")

    try:
        response = glue.start_job_run(
            JobName=GLUE_JOB_NAME,
            Arguments={
                "--S3_BUCKET_NAME": S3_BUCKET_NAME,
                "--RDS_HOST": RDS_HOST,
                "--RDS_PORT": RDS_PORT,
                "--RDS_DB": RDS_DB,
                "--RDS_USER": RDS_USER,
                "--RDS_PASSWORD": RDS_PASSWORD,
            },
        )
        job_run_id = response["JobRunId"]
        print(f"Glue job started: {job_run_id}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Glue job started", "file": key, "job_run_id": job_run_id}
            ),
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
