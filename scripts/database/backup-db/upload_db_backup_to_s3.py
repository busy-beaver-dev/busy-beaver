from datetime import datetime

import boto3

s3 = boto3.client("s3")

input_filename = "/tmp/data_dump.sql"
output_filename = "data_dump__{ts}.sql"
bucket_name = "busy-beaver"

ts = str(datetime.now().strftime("%Y%m%d_%H%M%S")).replace(".", "_")
s3.upload_file(input_filename, bucket_name, output_filename.format(ts=ts))
