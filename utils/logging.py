import logging
import datetime
from logging.handlers import TimedRotatingFileHandler

format_msg = logging.Formatter(u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.handlers.TimedRotatingFileHandler(
    f'logs/server/logs_info {datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    when='midnight',
    interval=1,
    encoding='utf-8')
file_handler.setFormatter(format_msg)

console_handler = logging.StreamHandler()
console_handler.setFormatter(format_msg)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
