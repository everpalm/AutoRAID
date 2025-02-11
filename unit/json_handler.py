# Contents of unit/json_handler.py
'''Copyright (c) 2024 Jaron Cheng'''
import json
import logging
import re
from unit.log_handler import get_logger

# Set up logger
logger = get_logger(__name__, logging.INFO)


def load_and_sort_json(file_path, key):
    '''docstring'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return sorted(data, key=lambda x: x[key])
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logger.error("Error loading or sorting file %s: %s", file_path, e)
        return []


def convert_size(callback):
    ''' Convert string that includes a number and unit in a dictionary
        e.g. convert 19.6k to 19.6 * 1024 = 20070.4
        Args: Dictionary
        Returns: Floats in a dictionary
        Raises: None
    '''
    def wrapper(*args, **kwargs):
        str_result = callback(*args, **kwargs)
        logger.debug(
                "Typte = %s, data to be converted = %s",
                type(str_result),
                str_result)
        pattern = r'(\d+(?:\.\d+)?)\D*([kKmMgG])'
        for key, value in str_result.items():
            logger.debug('key = %s, value = %s', key, value)
            # Only process IOPS and BW
            if key == 'IOPS' or key == 'BW':
                if value == 0:
                    continue
                match = re.search(pattern, value)
                logger.debug("match = %s", match)
                if match:
                    num = match.group(1)
                    unit = match.group(2)
                    logger.debug("num = %s, unit = %s", num, unit)
                    num = float(num)
                    if unit == 'K' or unit == 'k':
                        factor = 1024
                    elif unit == 'M':
                        factor = 1048576
                    elif unit == 'G':
                        factor = 1073741824
                    elif unit == 'T':
                        factor = 1099511627776
                    str_result[key] = num * factor
                else:
                    # pass
                    str_result[key] = float(value)
        return str_result
    return wrapper


def dict_format(callback):
    """
    Decorator to convert the result of a function (which should return an
    iterable) to a dictionary with integer keys (index).

    This decorator wraps a given function, executes it, logs the result,
    and then converts the iterable returned by the original function to a
    dictionary where keys are the integer indices of the iterable's elements.

    Args:
        original_function: The function to be wrapped.

    Returns:
        Callable: The wrapped function.
        dict:  A dictionary where the keys are integer indices of the input
        list. Returns None if an error occurs during the dictionary creation.
    Raises:
         TypeError: If the input is not iterable

    """
    def wrapper(*args, **kwargs):
        """
        Wrapper function that executes the original function and formats the
        result as a dictionary.

        Args:
            *args: Variable length argument list of the original function.
            **kwargs: Arbitrary keyword arguments of the original function.

        Returns:
            Dict[int, Any] | None: A dictionary where the keys are integer
            indices of the original function's iterable result.
            Returns None if an error occurs during processing or the input is
            not iterable.

        Raises:
            TypeError: If the input function result is not iterable
        """
        try:
            dict_result = callback(*args, **kwargs)
            logger.debug("Result to be transformed = %s", dict_result)
            return dict(enumerate(dict_result))
        except TypeError as e:
            logger.error("TypeError occurred in wrapper: %s", e)
        except Exception as e:
            logger.exception("An unexpected error occurred in wrapper: %s", e)
            raise
    wrapper.original = callback
    return wrapper
