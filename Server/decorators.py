from Server.settings import logger


def response_logger(func):
    def wrapper(*args, **kwargs):
        logger.debug(f'Calling function {func.__name__} with arguments {args} and keyword arguments {kwargs}')
        result = func(*args, **kwargs)
        logger.debug(f'Function {func.__name__} returned {result}')
        return result
    return wrapper
