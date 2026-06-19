from io import BytesIO

from botocore.exceptions import ClientError
from ..constants import env
from ..envvars import ENV_BUCKET
from ..logs import log_exception

import boto3


class S3File:
    """
    File wrapper class to access files in S3.
    """
    def __init__(self, path):
        self.bucket = env(ENV_BUCKET)
        self.s3_client = boto3.client("s3")
        self.key = path
        s3 = boto3.resource('s3')
        self.object = s3.Bucket(self.bucket).Object(self.key)

    def write(self, fi: BytesIO):
        fi.seek(0)
        data: bytes = fi.read()
        try:
            response = self.s3_client.put_object(Body=data, Key=self.key, Bucket=self.bucket)
        except ClientError as e:
            log_exception(__name__, e)
            raise e

    def read(self) -> bytes:
        """
        Gets the object.

        :return: The object data in bytes.
        """
        try:
            body = self.object.get()["Body"].read()
        except ClientError as e:
            log_exception(__name__, e)
            raise e
        else:
            return body

    def delete(self):
        """
        Deletes the object.
        """
        try:
            self.object.delete()
            self.object.wait_until_not_exists()
        except ClientError as e:
            log_exception(__name__, e)
            raise e
