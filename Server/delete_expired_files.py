import aioschedule as schedule
import asyncio
from datetime import timedelta
from django.utils import timezone
from Server.models.file_model import File
import os
from Server.settings import logger


async def delete_expired_files(expiration_days: int = 30):
    logger.info("Deleting expired files")
    for file in File.objects.filter(deleted_at__lt=timezone.now() - timedelta(days=expiration_days)):
        os.remove(file.file.path)
        file.delete()


async def main():
    logger.info("Starting scheduler")
    schedule.every(1).days.at("00:00").do(delete_expired_files)

    while True:
        logger.debug("Running scheduler")
        await schedule.run_pending()
        await asyncio.sleep(60*60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
