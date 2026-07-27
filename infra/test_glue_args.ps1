# One-off helper: writes Glue job run arguments to a JSON file (avoiding
# PowerShell's messy quoting rules for inline JSON), then starts the job.
$BUCKET = terraform output -raw bucket_name
$DBHOST = (terraform output -raw db_endpoint).Split(':')[0]
$DBPASS = terraform output -raw db_password

$argsObj = @{
    "--S3_BUCKET_NAME" = $BUCKET
    "--RDS_HOST"        = $DBHOST
    "--RDS_PORT"        = "5432"
    "--RDS_DB"          = "agri_climate"
    "--RDS_USER"        = "dbadmin"
    "--RDS_PASSWORD"    = $DBPASS
}

$json = $argsObj | ConvertTo-Json
[System.IO.File]::WriteAllText("$PWD\glue-args.json", $json, (New-Object System.Text.UTF8Encoding $false))

aws glue start-job-run --job-name agri-climate-risk-etl-job --arguments file://glue-args.json
