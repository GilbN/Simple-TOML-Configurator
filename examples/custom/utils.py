import logging
# simple logger function that takes log_level as argument and sets the log level
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

def configure_logging(log_level: str) -> None:
    """Configure logging for the application

    Args:
        log_level (str): Log level to set
    """
    if logger.getEffectiveLevel() == logging.getLevelName(log_level):
        return
    logger.setLevel(log_level)
    if log_level=="DEBUG":
        logger.debug(f"Debug logging enabled")
