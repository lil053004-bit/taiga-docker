"""
Taiga Custom Settings Extension
Extends Taiga's default settings to include custom app
"""
import os
import sys

# Add custom directory to Python path
CUSTOM_DIR = os.path.dirname(os.path.abspath(__file__))
if CUSTOM_DIR not in sys.path:
    sys.path.insert(0, CUSTOM_DIR)

# Import Taiga's default settings
try:
    from taiga.settings.common import *
    print("✓ Loaded Taiga base settings")
except ImportError:
    print("⚠ Could not import taiga.settings.common, using environment settings")
    pass

# Add custom app to INSTALLED_APPS
if 'INSTALLED_APPS' in dir():
    INSTALLED_APPS = list(INSTALLED_APPS) + ['custom']
    print("✓ Added 'custom' to INSTALLED_APPS")
else:
    INSTALLED_APPS = ['custom']

# Set default language to Chinese
LANGUAGE_CODE = 'zh-Hans'

# Get default user language from environment or use Chinese
DEFAULT_USER_LANGUAGE = os.getenv('DEFAULT_USER_LANGUAGE', 'zh-Hans')

print(f"✓ Custom settings loaded - Language: {LANGUAGE_CODE}")
print(f"✓ Default user language: {DEFAULT_USER_LANGUAGE}")
