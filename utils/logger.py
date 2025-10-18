# utils/logger.py
import logging

def get_logger():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler("test_run.log"),
                                  logging.StreamHandler()])
    return logging.getLogger()