import os

AUTO_ASSIGN_ADMIN_USERNAME = os.getenv('AUTO_ASSIGN_ADMIN_USERNAME', 'adsadmin')
AUTO_ASSIGN_ADMIN_EMAIL = os.getenv('AUTO_ASSIGN_ADMIN_EMAIL', 'lhweave@gmail.com')
AUTO_ASSIGN_ENABLED = os.getenv('AUTO_ASSIGN_ENABLED', 'True').lower() in ('true', '1', 'yes')

DEFAULT_USER_LANGUAGE = os.getenv('DEFAULT_USER_LANGUAGE', 'zh-Hans')

INSTALLED_APPS = INSTALLED_APPS + ['custom']

ROOT_URLCONF = getattr(globals().get('ROOT_URLCONF'), '__name__', 'taiga.urls')
try:
    from django.urls import include, path
    urlpatterns = globals().get('urlpatterns', [])
    urlpatterns.append(path('admin/custom/', include('custom.urls')))
except ImportError:
    pass

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
