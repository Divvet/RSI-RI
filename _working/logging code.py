import logging

# Define the log format
log_format = '[%(asctime)s] %(levelname)-8s %(name)-12s %(funcName)20s() %(lineno)s %(message)s'
# Define basic configuration
logging.basicConfig(level=logging.DEBUG, format=log_format, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)
