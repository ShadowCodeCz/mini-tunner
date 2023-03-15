logger_name = "mini.tunner.logger"

def default_logger_configuration(level="DEBUG"):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            logger_name: {
                'level': level,
                'propagate': False,
                'handlers': ['console_handler'],
            },
        },

        'handlers': {
            'console_handler': {
                'level': level,
                'formatter': 'simple',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
        },

        'formatters': {
            'generic': {
                'format': '%(asctime)s %(levelname)s %(message)s'
            },
            'simple': {
                'format': '%(message)s'
            }
        },
    }