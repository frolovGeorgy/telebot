from loguru import logger

logger.add("debug.log",
           format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>|<level>{level}</level> <level>{message}</level>',
           level='DEBUG',
           encoding='utf-8')
logger.add("errors.log",
           format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>|<level>{level}</level> <level>{message}</level>',
           level='ERROR',
           encoding='utf-8')
logger.add("info.log",
           format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>|<level>{level}</level> <level>{message}</level>',
           level='INFO',
           encoding='utf-8')

# decorator for catching any exceptions
my_log = logger.catch
