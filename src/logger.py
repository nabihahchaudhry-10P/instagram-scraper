import logging

class MyLogger:
    def __init__(self, log_file='app.log', level=logging.DEBUG):
        logging.basicConfig(filename=log_file, level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    def debug(self, message):
        logging.debug(message)

    def info(self, message):
        logging.info(message)

    def warning(self, message):
        logging.warning(message)

    def error(self, message):
        logging.error(message)

    def critical(self, message):
        logging.critical(message)
