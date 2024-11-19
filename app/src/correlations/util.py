import logging
import time
from functools import wraps


def time_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"'{func.__name__}': {duration:.4f} seconds")
        return result

    return wrapper
