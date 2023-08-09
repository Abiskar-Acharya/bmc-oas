import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(module)s]: [%(message)s]")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

fileHandler = RotatingFileHandler("logs.log")
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)