import logging

def get_logger(name: str):
    """
    Returns a configured logger instance.
    """
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    if not log.handlers:
        log.addHandler(console_handler)

    return log