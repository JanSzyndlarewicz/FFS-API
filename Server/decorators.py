import time
import traceback

from Server.settings import logger


def response_logger(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.debug(f'Function {func.__module__}.{func.__qualname__} with arguments {args} and '
                         f'keyword arguments {kwargs} returned {result} in {elapsed_time} seconds')
            return result
        except Exception as e:
            logger.error(f'Function {func.__module__}.{func.__qualname__} with arguments {args} and '
                         f'keyword arguments {kwargs} threw an exception: {str(e)}\n{traceback.format_exc()}')
            raise e
    return wrapper
