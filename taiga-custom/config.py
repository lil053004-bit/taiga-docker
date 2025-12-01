"""
Taiga Custom App Configuration
This file extends Taiga's settings to register the custom app and enable custom management commands.
"""

# Register the custom app so Django recognizes our management commands
INSTALLED_APPS = [
    'custom',
]

# Custom app settings
AUTO_ASSIGN_ADMIN_USERNAME = None
AUTO_ASSIGN_ADMIN_EMAIL = None
AUTO_ASSIGN_ENABLED = True
DEFAULT_USER_LANGUAGE = 'zh-Hans'
