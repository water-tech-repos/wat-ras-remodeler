"""
Helper functions for filesystems.
For S3 access, the following environment vairables can be set and picked up for authentication:
 - AWS_ACCESS_KEY_ID
 - AWS_SECRET_ACCESS_KEY
 - AWS_SESSION_TOKEN
For Azure blob storage the following enviornment variables can be set and picked up for authentication:
 - AZURE_STORAGE_CONNECTION_STRING
 - AZURE_STORAGE_ACCOUNT_NAME
 - AZURE_STORAGE_ACCOUNT_KEY
 - AZURE_STORAGE_SAS_TOKEN
 - AZURE_STORAGE_CLIENT_SECRET
 - AZURE_STORAGE_CLIENT_ID
 - AZURE_STORAGE_TENANT_ID

 String and bytes functions will store the data in memory. The file functions will create temporary files so as to not
 run out of memory.
 """
import tempfile
from typing import BinaryIO
from typing import Iterator, Union
import uuid
import os
import fsspec


def read_in_chunks(file_obj: Union[BinaryIO, fsspec.core.OpenFile], size_in_bytes: int = 10000000) -> Iterator[bytes]:
    """Generator function to read file in chunks to not run out of memory

    Args:
        file_obj (Union[BinaryIO, fsspec.OpenFile]): file to read in chunks
        size_in_bytes (int, optional): max number of bytes to read per chunk. Defaults to 10 MB.

    Yields:
        Iterator[bytes]: iterator of chunks of bytes
    """
    while True:
        chunk = file_obj.read(size_in_bytes)
        if not chunk:
            break
        yield chunk


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


def get_file(src_uri: Union[str, None] = None, ext: str = "") -> str:
    """Get a local filepath string copied from a URI. Can be local filesystem, S3 or Azure blob storage. A path to a
    temporary file will be returned pointing to the created temp file on the local file system. Large files are copied
    in chunks to avoid running out of memory. If src_uri is None, a temp filepath will be returned, but no file is
    created. You should delete the temp files when you are done with them.

    Args:
        src_uri (Union[str, None]): URI to the source file or None. If None, a temp filepath will be returned (but no
        file is created).
        For S3 use:
         - s3://<bucket_name>/<key_name>
        For Azure use:
         - abfs://<container_name>/<key_name>
        For local files use the filesystem path.
        ext (str): extension to use (e.g. .hdf). Default is empty string. If empty and src_uri is not None, extension
        will be copied from src_uri

    Returns:
        str: path to temp file with data from URI
    """
    # some file types require the extension to match
    if src_uri is not None and len(os.path.splitext(src_uri)) == 2 and ext == "":
        ext = os.path.splitext(src_uri)[1]
    temp_file_path = os.path.join(
        tempfile.gettempdir(), str(uuid.uuid4())) + ext
    if src_uri:
        with fsspec.open(src_uri, 'rb') as src_file, fsspec.open(temp_file_path, 'wb') as temp_file:
            for chunk in read_in_chunks(src_file):
                temp_file.write(chunk)
    return temp_file_path


def put_file(src_uri: str, dst_uri: str) -> None:
    """Copy data at a URI to another URI. Can be local filesystem, S3 or Azure blob storage.

    Args:
        src_uri (str): source uri to read from
        dst_uri (str): destination uri to write the file
    """
    with fsspec.open(src_uri, 'rb') as src_file, fsspec.open(dst_uri, 'wb') as dst_file:
        for chunk in read_in_chunks(src_file):
            dst_file.write(chunk)
