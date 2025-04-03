import unittest
from unittest.mock import patch, MagicMock

from botocore.exceptions import ClientError

from app.src.fetcher.s3 import S3Connector


class S3ConnectorTestCase(unittest.TestCase):
    @patch("boto3.client")
    @patch("boto3.resource")
    def setUp(self, mock_boto_resource, mock_boto_client):
        """Set up a mock S3Connector instance with patched boto3."""
        # Set up mock client and resource
        self.mock_client = MagicMock()
        self.mock_resource = MagicMock()
        mock_boto_client.return_value = self.mock_client
        mock_boto_resource.return_value = self.mock_resource

        # Configure client exceptions
        self.mock_client.exceptions = MagicMock()
        self.mock_client.exceptions.ClientError = ClientError

        # Create the connector with mocked dependencies
        self.connector = S3Connector(
            endpoint_url="http://mock-s3-url.com",
            access_key="mock-access-key",
            secret_key="mock-secret-key",
            region_name="mock-region"
        )

    def test_upload_file_success(self):
        """Test successful file upload."""
        # Simulate no existing file (404 error)
        error_response = {'Error': {'Code': '404'}}
        self.mock_client.head_object.side_effect = ClientError(error_response, 'HeadObject')

        # Test upload
        result = self.connector.upload_file("mock_file.txt", "mock_bucket", replace=False)
        self.assertTrue(result, "File upload should succeed")
        self.mock_client.upload_file.assert_called_once()

    def test_upload_file_exists(self):
        """Test upload failure when file already exists."""
        # Simulate existing file
        self.mock_client.head_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        result = self.connector.upload_file("mock_file.txt", "mock_bucket", replace=False)
        self.assertFalse(result, "File upload should fail if file exists and replace=False")
        self.mock_client.upload_file.assert_not_called()

    def test_upload_file_with_replace(self):
        """Test successful file upload with replace=True."""
        result = self.connector.upload_file("mock_file.txt", "mock_bucket", replace=True)
        self.assertTrue(result, "File upload with replace=True should succeed")
        self.mock_client.upload_file.assert_called_once()

    def test_download_file_success(self):
        """Test successful file download."""
        result = self.connector.download_file("mock_bucket", "mock_object.txt", "local_mock_file.txt")
        self.assertTrue(result, "File download should succeed")
        self.mock_client.download_file.assert_called_once()

    def test_download_file_failure(self):
        """Test download failure due to an exception."""
        # Simulate download failure
        self.mock_client.download_file.side_effect = Exception("Download failed")

        result = self.connector.download_file("mock_bucket", "mock_object.txt", "local_mock_file.txt")
        self.assertFalse(result, "File download should fail if an exception occurs")


if __name__ == '__main__':
    unittest.main()
