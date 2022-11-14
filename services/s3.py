from decouple import config
import boto3
from fastapi.exceptions import HTTPException 

class S3Service:
    def __init__(self):
        self.key = config("AWS_ACCESS_KEY")
        self.secret = config("AWS_SECRET")
        # with this credential we have full access from the library
        self.s3 = boto3.client("s3", aws_access_key_id=self.key, aws_secret_access_key=self.secret)
        self.bucket = config("AWS_BUCKET_NAME")
        self.region = config("AWS_REGION")
    
    def upload(self, path, key, ext):
        try:
            self.s3.upload_file(path, self.bucket, key, ExtraArgs={"ACL": "public-read", "ContentType": f"image/{ext}"})
            print(ext)
            return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
        except Exception as ex:
            raise HTTPException(500, "S3 is not available")