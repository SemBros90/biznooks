"""Initialize MinIO bucket for local dev. Connects via boto3 using S3_ENDPOINT_URL env.

Usage in docker-compose as an init job or run locally:
  python scripts/init_minio.py
"""
import os
import time
import boto3
from botocore.client import Config

BUCKET = os.getenv('S3_BUCKET', 'biznooks-demo')
ENDPOINT = os.getenv('S3_ENDPOINT_URL', 'http://minio:9000')
AWS_KEY = os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin')
AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin')

def main():
    # wait for endpoint to be available
    for _ in range(20):
        try:
            s3 = boto3.resource('s3', endpoint_url=ENDPOINT, aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET, config=Config(signature_version='s3v4'))
            # Try listing buckets to check connectivity
            list(s3.buckets.all())
            break
        except Exception:
            time.sleep(1)
    try:
        bucket = s3.Bucket(BUCKET)
        if bucket.creation_date is None:
            s3.create_bucket(Bucket=BUCKET)
            print('Created bucket:', BUCKET)
        else:
            print('Bucket already exists:', BUCKET)
    except Exception as e:
        print('Failed to create bucket:', e)


if __name__ == '__main__':
    main()
