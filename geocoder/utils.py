import logging
from pathlib import Path

def create_logger(log_file: Path, name: str = "LOGS", level: int = logging.DEBUG) -> logging.Logger:
    log_file = Path(log_file)
    logger = logging.getLogger(name)
    logger.setLevel(level)  
    file_handler = logging.FileHandler(log_file, mode = "w")
    console_handler = logging.StreamHandler()

    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
