import os

AUTO_ASSIGN_ADMIN_USERNAME = os.getenv('AUTO_ASSIGN_ADMIN_USERNAME', 'adsadmin')
AUTO_ASSIGN_ADMIN_EMAIL = os.getenv('AUTO_ASSIGN_ADMIN_EMAIL', 'lhweave@gmail.com')
AUTO_ASSIGN_ENABLED = os.getenv('AUTO_ASSIGN_ENABLED', 'True').lower() in ('true', '1', 'yes')

INSTALLED_APPS = INSTALLED_APPS + ['custom']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/taiga-back/logs/auto_assign.log',
        },
    },
    'loggers': {
        'custom': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}
