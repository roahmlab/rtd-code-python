import logging.config



def config_logger(level: str = 'WARN'):
    '''
    Configures the logger with the specified 
    logging level
    '''
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default_handler': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'standard',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default_handler'],
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(logging_config)