import io
import os
import subprocess
import tarfile
import uuid
from io import BytesIO
from time import sleep
from typing import Tuple

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


def encrypt_file(path, password: str) -> tuple[BytesIO, str] | tuple[None, None]:
    path = zip_file_with_password(path, password)
    try:
        with open(path, 'rb') as f:
            encrypted_file = io.BytesIO(f.read())
            return encrypted_file, path
    except FileNotFoundError as e:
        print(e)
        return None, None


def zip_file_with_password(source_path: str, password: str) -> str | None:
    zip_filename = os.path.basename(source_path) + '.zip'
    non_secured_filename = os.path.basename(source_path)
    current_dir = os.getcwd()
    os.chdir(os.path.dirname(source_path))

    zip_command = ["zip", "-r", "-P", password, zip_filename, non_secured_filename]

    try:
        subprocess.run(zip_command, check=True)
        while not os.path.exists(zip_filename):
            sleep(0.1)
        path_to_zipfile = os.path.abspath(zip_filename)
        os.chdir(current_dir)
        return path_to_zipfile
    except subprocess.CalledProcessError as e:
        print(e)
        return None


def get_file_from_path(file_path: str) -> (str, bytes):
    """
    Get the file content from the given file path.
    :param file_path: Path to the file
    :return: Tuple containing the file name as string and the file content in bytes
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
