import aioschedule as schedule
import asyncio
from datetime import timedelta
from django.utils import timezone
from Server.models.file_model import File
import os
from Server.settings import logger


async def delete_expired_files(expiration_days: int = 30) -> None:
    """
    Delete files that have been in the trash for more than the given number of days.
    :param expiration_days: Number of days after which the file is considered expired
    :return: None
    """
    logger.info("Deleting expired files")
    for file in File.objects.filter(deleted_at__lt=timezone.now() - timedelta(days=expiration_days)):
        os.remove(file.file.path)
        file.delete()


def delete_files_not_connected_to_db() -> None:
    """
    Find files that are not connected to the database. Delete them.
    :return: None
    """
    logger.info("Finding files not connected to the database")
    for file in os.listdir("uploads"):
        if not File.objects.filter(file=file):
            os.remove(file)
            logger.info(f"Found file that was not connected to the database. Deleted file: \"{file}\"")


def delete_files_not_in_uploads_folder() -> None:
    """
    Find files that are not in the uploads folder. Delete them.
    :return: None
    """
    logger.info("Finding files not in the uploads folder")
    for file in File.objects.all():
        if not os.path.exists(file.file.path):
            file.delete()
            logger.info(f"Found file that was not in the uploads folder. Deleted file: \"{file.file.path}\"")


async def main():
    """
    Main function to run the scheduler.
    """
    logger.info("Starting scheduler")
    schedule.every(1).days.at("00:00").do(delete_expired_files)
    schedule.every(1).days.at("00:00").do(delete_files_not_connected_to_db)
    schedule.every(1).days.at("00:00").do(delete_files_not_in_uploads_folder)

    while True:
        logger.debug("Running scheduler")
        await schedule.run_pending()
        await asyncio.sleep(60 * 60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
