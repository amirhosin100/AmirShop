from .settings import *

#settings configuration for testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,  #disable all logs
    'formatters': {
        'verbose': {
            'format': '',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'CRITICAL',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'CRITICAL',
    }
}
