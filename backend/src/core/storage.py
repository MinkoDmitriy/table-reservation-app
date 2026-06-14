import os
import uuid
import abc
import aioboto3
from fastapi import UploadFile, HTTPException, status
from src.core.config import settings

class BaseStorage(abc.ABC):
    @abc.abstractmethod
    async def upload_file(self, file: UploadFile) -> str:
        """Загружает файл и возвращает путь или URL для доступа к нему"""
        pass

    @abc.abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Удаляет файл из хранилища"""
        pass


class LocalStorage(BaseStorage):
    def __init__(self, upload_dir: str = "static/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_file(self, file: UploadFile) -> str:
        _, ext = os.path.splitext(file.filename)
        filename = f"{uuid.uuid4().hex}{ext.lower()}"
        file_path = os.path.join(self.upload_dir, filename)
        
        try:
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Не удалось сохранить файл в локальное хранилище: {str(e)}"
            )
        return f"/static/uploads/{filename}"

    async def delete_file(self, file_path: str) -> bool:
        relative_path = file_path.lstrip("/")
        if os.path.exists(relative_path):
            try:
                os.remove(relative_path)
                return True
            except OSError:
                return False
        return False


class S3Storage(BaseStorage):
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket_name = settings.S3_BUCKET_NAME
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.region_name = settings.S3_REGION
        self.aws_access_key_id = settings.S3_ACCESS_KEY
        self.aws_secret_access_key = settings.S3_SECRET_KEY
        self.public_url = settings.S3_PUBLIC_URL or settings.S3_ENDPOINT_URL

        if not self.bucket_name or not self.endpoint_url:
            raise ValueError("S3_BUCKET_NAME and S3_ENDPOINT_URL must be configured when STORAGE_TYPE is 's3'")

    async def init_bucket(self):
        """Проверяет существование бакета, создает его при отсутствии и настраивает публичную read-only политику."""
        import json
        async with self.session.client(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url
        ) as s3:
            try:
                await s3.head_bucket(Bucket=self.bucket_name)
            except Exception:
                try:
                    await s3.create_bucket(Bucket=self.bucket_name)
                    print(f"Bucket '{self.bucket_name}' created successfully.")
                except Exception as e:
                    print(f"Failed to create bucket '{self.bucket_name}': {e}")
                    raise e

            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                    }
                ]
            }
            try:
                await s3.put_bucket_policy(
                    Bucket=self.bucket_name,
                    Policy=json.dumps(policy)
                )
                print(f"Public read policy applied to bucket '{self.bucket_name}'.")
            except Exception as e:
                print(f"Failed to set bucket policy: {e}")
                raise e


    async def upload_file(self, file: UploadFile) -> str:
        _, ext = os.path.splitext(file.filename)
        filename = f"uploads/{uuid.uuid4().hex}{ext.lower()}"
        
        async with self.session.client(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url
        ) as s3:
            try:
                file_content = await file.read()
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=file_content,
                    ContentType=file.content_type
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Не удалось загрузить файл в S3: {str(e)}"
                )
        
        public_endpoint = self.public_url.rstrip("/")
        return f"{public_endpoint}/{self.bucket_name}/{filename}"

    async def delete_file(self, file_path: str) -> bool:
        try:
            key = file_path.split(f"/{self.bucket_name}/")[-1]
        except Exception:
            return False
            
        async with self.session.client(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url
        ) as s3:
            try:
                await s3.delete_object(Bucket=self.bucket_name, Key=key)
                return True
            except Exception:
                return False


def get_storage() -> BaseStorage:
    if settings.STORAGE_TYPE.lower() == "s3":
        return S3Storage()
    return LocalStorage()
