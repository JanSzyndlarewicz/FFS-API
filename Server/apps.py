import asyncio
from concurrent.futures import ThreadPoolExecutor
from django.apps import AppConfig


class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Server'

    def ready(self):
        from Server.utils.file_cleaner import main

        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())

        executor = ThreadPoolExecutor()
        loop = asyncio.new_event_loop()
        executor.submit(start_loop, loop)
