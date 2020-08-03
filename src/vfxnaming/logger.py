# coding=utf-8
from __future__ import absolute_import, print_function

import logging
import sys
import os
import json
from datetime import date

_base_name = "vfxnaming"
logger = logging.getLogger(name='{}log'.format(_base_name))


def init_logger():
    """Initialize '{}log' logging object and add a STDOUT handler to output to console, terminal, etc.
    """.format(_base_name)
    logger.setLevel(logging.DEBUG)

    found_handler = False
    for each in logger.handlers:
        if isinstance(each, logging.StreamHandler):
            found_handler = True
            break

    if not found_handler:
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s:%(module)s:%(funcName)s:'
            '%(lineno)s:%(levelname)s] %(message)s'
        )
        # STDOUT stream
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setLevel(logging.DEBUG)
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)


def init_file_logger():
    """Adds file log to '{}log' logging object. Log files will be located at the user OS folder.

    Raises:
        OSError, IOError: Directory for log files couldn't be created.

    Returns:
        [str]: Log file path
    """.format(_base_name)

    found_handler = False
    for each in logger.handlers:
        if isinstance(each, logging.FileHandler):
            found_handler = True
            break

    if not found_handler:
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s:%(module)s:%(funcName)s:'
            '%(lineno)s:%(levelname)s] %(message)s'
        )
        # Log file stream
        userPath = os.path.expanduser("~")
        module_dir = os.path.split(__file__)[0]
        config_location = os.path.join(module_dir, "cfg", "config.json")
        config = dict()
        with open(config_location) as fp:
            config = json.load(fp)
        finalDir = os.path.join(userPath, "." + config["logger_dir_name"])

        try:
            if not os.path.exists(finalDir):
                os.mkdir(finalDir)
        except (OSError, IOError) as why:
            raise why

        today = date.today()
        date_string = today.strftime("%d-%m-%Y")
        log_file_path = os.path.join(finalDir, '{}_{}.log'.format(_base_name, date_string))
        fileHandler = logging.FileHandler(log_file_path, mode='a')
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

        return log_file_path
    return None
