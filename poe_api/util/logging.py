import logging

level = logging.DEBUG

# format logging schema and colors
class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self):
        super().__init__()        

    def format(self, record):
        fmt = '%(levelname)s:\t%(msg)s | %(asctime)s | %(filename)s:%(lineno)2d'

        self.FORMATS = {
            logging.DEBUG: self.yellow + fmt + self.reset,
            logging.INFO: self.blue + fmt + self.reset,
            logging.WARNING: self.yellow + fmt + self.reset,
            logging.ERROR: self.red + fmt + self.reset,
            logging.CRITICAL: self.bold_red + fmt + self.reset
        }

        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record) 

# with this method we can create new loggers by name
def getLogger(name):
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    module_logger = logging.getLogger(name)
    module_logger.propagate = False
    module_logger.addHandler(handler)
    module_logger.setLevel(level=level)
    module_logger.debug("new logger appended",extra={"scope":"initiation"})


    return module_logger

logger = getLogger(__name__)
