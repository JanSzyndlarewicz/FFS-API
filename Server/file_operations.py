import io
import tarfile
from Server.models import UploadedFile


def create_tarfile_from_file_contents(files: list[UploadedFile]) -> io.BytesIO:
    """
    Create a tar file from the contents of the files.
    :param files: list of UploadedFile objects
    :return: file-like object containing the tar file
    """
    tar_stream = io.BytesIO()

    with tarfile.open(fileobj=tar_stream, mode='w:gz') as tar:
        for file in files:
            file_content = file.file_content
            file_name = file.file.name
            file_obj = io.BytesIO(file_content)

            # Create a TarInfo object for the file
            info = tarfile.TarInfo(name=file_name)
            info.size = len(file_content)

            tar.addfile(info, file_obj)

    tar_stream.seek(0)

    return tar_stream
