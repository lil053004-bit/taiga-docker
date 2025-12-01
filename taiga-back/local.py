# Taiga Backend Local Configuration
# This file extends Taiga's default settings
import os

# Add custom app to INSTALLED_APPS
INSTALLED_APPS = INSTALLED_APPS + ['custom']

# Auto-assign settings from environment
AUTO_ASSIGN_ADMIN_USERNAME = os.getenv('AUTO_ASSIGN_ADMIN_USERNAME', 'adsadmin')
AUTO_ASSIGN_ADMIN_EMAIL = os.getenv('AUTO_ASSIGN_ADMIN_EMAIL', 'lhweave@gmail.com')
AUTO_ASSIGN_ENABLED = os.getenv('AUTO_ASSIGN_ENABLED', 'True') == 'True'
DEFAULT_USER_LANGUAGE = os.getenv('DEFAULT_USER_LANGUAGE', 'zh-Hans')

# Ensure Chinese as default
LANGUAGE_CODE = 'zh-Hans'

# Enable logging for custom app
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/taiga-back/logs/custom.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'custom': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

print("=" * 60)
print("✓ Custom Taiga Local Configuration Loaded")
print(f"  - Custom app added to INSTALLED_APPS")
print(f"  - Auto-assign enabled: {AUTO_ASSIGN_ENABLED}")
print(f"  - Admin username: {AUTO_ASSIGN_ADMIN_USERNAME}")
print(f"  - Default language: {DEFAULT_USER_LANGUAGE}")
print("=" * 60)
