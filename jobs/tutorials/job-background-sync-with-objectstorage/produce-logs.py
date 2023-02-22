import logging
import time
import os
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler


def create_rotating_log(path):
    """"""
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)

    # handler = TimedRotatingFileHandler(path, when="m", interval=1, backupCount=5)
    handler = RotatingFileHandler(path, maxBytes=20, backupCount=5)
    logger.addHandler(handler)

    for i in range(10):
        logger.info("This is a test, with mb large log files!")
        time.sleep(2)


# ----------------
if __name__ == "__main__":
    print('Start creating rotating logs')
    
    dirname = os.path.dirname(os.path.abspath(__file__)) + "/logs/"
    log_file = os.path.join(dirname, "test.log")

    create_rotating_log(log_file)
