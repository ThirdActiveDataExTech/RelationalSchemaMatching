import logging
import os
from typing import Optional, Tuple, Any

import boto3
from botocore.client import Config, BaseClient


class S3Connector:
    """
    AWS S3 및 MinIO와 같은 S3 호환 스토리지 서비스에 대한 연결을 처리하는 클래스입니다.
    파일 업로드 및 다운로드와 같은 일반적인 작업을 위한 메서드를 제공합니다.
    """

    def __init__(
            self,
            endpoint_url: Optional[str] = None,
            access_key: Optional[str] = None,
            secret_key: Optional[str] = None,
            region_name: Optional[str] = None,
            signature_version: str = 's3v4'
    ):
        """
        연결 매개변수를 사용하여 커넥터를 초기화합니다.

        Args:
            endpoint_url: S3 호환 서비스의 URL (MinIO의 경우 필수, AWS S3의 경우 선택 사항)
            access_key: AWS 액세스 키 ID 또는 MinIO 액세스 키
            secret_key: AWS 비밀 액세스 키 또는 MinIO 비밀 키
            region_name: S3 서비스의 리전 이름 (AWS S3의 경우 필수, MinIO의 경우 선택 사항)
            signature_version: 인증을 위한 S3 서명 버전
        """
        self.endpoint_url = endpoint_url or os.environ.get('MINIO_ENDPOINT_URL')
        self.access_key = access_key or os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_key = secret_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.region_name = region_name
        self.signature_version = signature_version

        # Initialize the connection
        self.s3_client, self.s3_resource = self._initialize_connection()

    def _initialize_connection(self) -> Tuple[BaseClient, Any]:
        """S3 클라이언트 및 리소스 객체를 초기화합니다."""
        config = Config(signature_version=self.signature_version)

        # Create the client
        client_kwargs = {
            'aws_access_key_id': self.access_key,
            'aws_secret_access_key': self.secret_key,
            'region_name': self.region_name,
            'config': config
        }

        # Add endpoint URL if it's provided (necessary for MinIO)
        if self.endpoint_url:
            client_kwargs['endpoint_url'] = self.endpoint_url

        s3_client = boto3.client('s3', **client_kwargs)
        s3_resource = boto3.resource('s3', **client_kwargs)

        return s3_client, s3_resource

    def upload_file(self, file_path: str, bucket_name: str, object_name: Optional[str] = None, replace: bool = False):
        """
        S3 호환 스토리지에 파일을 업로드합니다.

        Args:
            file_path: 업로드할 로컬 파일 경로
            bucket_name: 대상 버킷 이름
            object_name: S3에서 파일의 키 이름 (지정하지 않으면 기본적으로 파일 이름 사용)
            replace: 동일한 이름의 파일이 있을 경우 덮어쓸지 여부 (기본값: False)

        Returns:
            업로드가 성공하면 True, 그렇지 않으면 False를 반환합니다.
        """
        if not object_name:
            object_name = os.path.basename(file_path)

        try:
            # 파일이 이미 존재하는지 확인
            if not replace:
                try:
                    self.s3_client.head_object(Bucket=bucket_name, Key=object_name)
                    logging.error(
                        f"File '{object_name}' already exists in bucket '{bucket_name}'. Use replace=True to overwrite.")
                    return False
                except self.s3_client.exceptions.ClientError as e:
                    # 파일이 존재하지 않을 경우 계속 진행
                    if e.response['Error']['Code'] != '404':
                        logging.error(f"Error checking file existence: {e}")
                        return False

            # 파일 업로드
            self.s3_client.upload_file(file_path, bucket_name, object_name)
            logging.info(f"File '{file_path}' successfully uploaded to {bucket_name}/{object_name}")
            return True
        except Exception as e:
            logging.error(f"Error uploading file: {e}")
            return False

    def download_file(self, bucket_name: str, object_name: str, file_path: str):
        """
        S3 호환 스토리지에서 파일을 다운로드합니다.

        Args:
            bucket_name: 소스 버킷 이름
            object_name: S3에서 파일의 키 이름
            file_path: 파일이 저장될 로컬 경로

        Returns:
            다운로드가 성공하면 True, 그렇지 않으면 False를 반환합니다.
        """
        try:
            self.s3_client.download_file(bucket_name, object_name, file_path)
            logging.info(f"File '{object_name}' successfully downloaded from {bucket_name} to {file_path}")
            return True
        except Exception as e:
            logging.error(f"Error downloading file: {e}")
            return False
