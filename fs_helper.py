"""
Helper functions for filesystems.
For S3 access, the following environment vairables can be set and picked up for authentication:
 - AWS_ACCESS_KEY_ID
 - AWS_SECRET_ACCESS_KEY
For Azure blob storage the following enviornment variables can be set and picked up for authentication:
 - AZURE_STORAGE_CONNECTION_STRING
 - AZURE_STORAGE_ACCOUNT_NAME
 - AZURE_STORAGE_ACCOUNT_KEY
 - AZURE_STORAGE_SAS_TOKEN
 - AZURE_STORAGE_CLIENT_SECRET
 - AZURE_STORAGE_CLIENT_ID
 - AZURE_STORAGE_TENANT_ID
 """
import tempfile
from typing import BinaryIO
import fsspec


def get_bytes(src_uri: str) -> bytes:
    """Get bytes object from a URI. Can be local filesystem, S3 or Azure blob storage.

    Args:
        src_uri (str): URI to the file.
        For S3 use:
         - s3://<bucket_name>/<key_name>
        For Azure use:
         - abfs://<container_name>/<key_name>
        For local files use the filesystem path.

    Returns:
        bytes: bytes object of the file's data
    """
    with fsspec.open(src_uri, 'rb') as file:
        return file.read()


def put_bytes(src_bytes: bytes, dst_uri: str) -> None:
    """Write bytes object to a URI. Can be local filesystem, S3 or Azure blob storage.

    Args:
        src_bytes (bytes): bytes object to write
        dst_uri (str): destination uri to write the file
    """
    with fsspec.open(dst_uri, 'wb') as file:
        file.write(src_bytes)


def get_string(src_uri: str) -> str:
    """Get string object from a URI. Can be local filesystem, S3 or Azure blob storage.

    Args:
        src_uri (str): URI to the file.
        For S3 use:
         - s3://<bucket_name>/<key_name>
        For Azure use:
         - abfs://<container_name>/<key_name>
        For local files use the filesystem path.

    Returns:
        str: string object of the file's data
    """
    with fsspec.open(src_uri, 'r') as file:
        return file.read()


def put_string(src_str: str, dst_uri: str) -> None:
    """Write string object to a URI. Can be local filesystem, S3 or Azure blob storage.

    Args:
        src_str (str): string object to write
        dst_uri (str): destination uri to write the file
    """
    with fsspec.open(dst_uri, 'w') as file:
        file.write(src_str)


def get_file(src_uri: str) -> BinaryIO:
    """Get file object from a URI. Can be local filesystem, S3 or Azure blob storage. You must close it when you are
    done with it!

    Args:
        src_uri (str): URI to the file.
        For S3 use:
         - s3://<bucket_name>/<key_name>
        For Azure use:
         - abfs://<container_name>/<key_name>
        For local files use the filesystem path.

    Returns:
        BinaryIO: file like object of the file's data
    """
    file = tempfile.TemporaryFile()
    with fsspec.open(src_uri, 'rb') as src_file:
        file.write(src_file.read())
    return file


def put_file(src_file: BinaryIO, dst_uri: str) -> None:
    """Write file object to a URI. Can be local filesystem, S3 or Azure blob storage.

    Args:
        src_file (BinaryIO): file like object to write
        dst_uri (str): destination uri to write the file
    """
    with fsspec.open(dst_uri, 'wb') as file:
        file.write(src_file.read())
