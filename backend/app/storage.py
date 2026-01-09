import os
from typing import Optional


class StorageError(Exception):
    pass


class Storage:
    """Simple storage adapter supporting S3 (boto3) or local filesystem fallback.

    Configuration via env:
    - `S3_BUCKET` and AWS credentials in env will enable S3.
    - Otherwise files are written under `backend/storage/`.
    """

    def __init__(self):
        self.bucket = os.getenv('S3_BUCKET')
        self.s3_region = os.getenv('AWS_REGION')
        self.s3_client = None
        if self.bucket:
            try:
                import boto3
                self.s3_client = boto3.client('s3')
            except Exception:
                self.s3_client = None

        self.local_base = os.path.join(os.path.dirname(__file__), '..', 'storage')
        os.makedirs(self.local_base, exist_ok=True)

    def upload_bytes(self, key: str, data: bytes, content_type: Optional[str] = None) -> str:
        """Upload bytes and return a URL or path."""
        if self.s3_client and self.bucket:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            try:
                self.s3_client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra_args)
                # return S3 URL (may be friendly for public buckets)
                return f"s3://{self.bucket}/{key}"
            except Exception as e:
                raise StorageError(str(e))

        # fallback to local filesystem
        path = os.path.join(self.local_base, key)
        ddir = os.path.dirname(path)
        os.makedirs(ddir, exist_ok=True)
        try:
            with open(path, 'wb') as f:
                f.write(data)
        except Exception as e:
            raise StorageError(str(e))
        return path

    def presign_upload(self, key: str, expires_in: int = 3600) -> dict:
        """Return a presigned PUT URL and headers for direct browser upload.

        Returns: {"url": <put_url>, "headers": {}} or raises StorageError.
        """
        if not self.s3_client or not self.bucket:
            raise StorageError('S3 client not configured')
        try:
            params = {'Bucket': self.bucket, 'Key': key}
            url = self.s3_client.generate_presigned_url('put_object', Params=params, ExpiresIn=expires_in)
            return {'url': url, 'headers': {}}
        except Exception as e:
            raise StorageError(str(e))


storage = Storage()
