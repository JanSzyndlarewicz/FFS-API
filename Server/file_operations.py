import io
import os
import tarfile


def create_tarfile_in_memory(files: list) -> io.BytesIO:
    """
    Create a tarfile in memory from a list of files.
    :param files: list of files
    :return: tar file that contains the files
    """
    tar_data = io.BytesIO()
    with tarfile.open(fileobj=tar_data, mode='w:gz') as tar:
        for file in files:
            tar.add(file, arcname=os.path.basename(file))
    tar_data.seek(0)
    return tar_data

