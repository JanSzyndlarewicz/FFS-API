import io
import os
import tarfile
import uuid
import pyzipper
from Server.models import File


def create_tarfile_in_memory(files: list) -> io.BytesIO:
    """
    Create a tarfile in memory from a list of files.
    :param files: list of files
    :return: tar file that contains the files
    """
    tar_data = io.BytesIO()
    with tarfile.open(fileobj=tar_data, mode='w:gz') as tar:
        for file in files:
            try:
                if os.path.isfile(file):
                    tar.add(file, arcname=os.path.basename(file))
            except FileNotFoundError as e:
                print(e)
    tar_data.seek(0)
    return tar_data


def encrypt_file(path, content, password: str) -> io.BytesIO:
    encrypted_file = io.BytesIO()
    with pyzipper.AESZipFile(encrypted_file, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
        zf.pwd = password.encode()
        zf.writestr(path, content)
    encrypted_file.seek(0)
    return encrypted_file


def get_file_from_path(file_path: str):
    """
    Get the file content from the given file path.
    :param file_path: Path to the file
    :return: File object
    """
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return os.path.basename(file_path), f.read()
    else:
        return None


def generate_unique_access_token() -> str:
    """
    Generate a unique access token for the file.
    :return: String containing the access token for the file
    """
    if File.objects.filter(access_token=uuid.uuid4().hex).exists():
        return generate_unique_access_token()
    return uuid.uuid4().hex
