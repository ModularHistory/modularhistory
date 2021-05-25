"""Admin-related settings."""
from decouple import config

from core.environment import ENVIRONMENT

# https://github.com/cdrx/django-admin-menu
ADMIN_LOGO = 'logo_head_white.png'

# https://django-admin-tools.readthedocs.io/en/latest/customization.html
ADMIN_TOOLS_MENU = 'apps.admin.admin_menu.AdminMenu'
ADMIN_TOOLS_THEMING_CSS = 'styles/admin.css'

# https://github.com/dizballanze/django-admin-env-notice
ENVIRONMENT_NAME = f'{ENVIRONMENT.title()} server'
ENVIRONMENT_COLOR = '#FF2222'

# https://github.com/dmpayton/django-admin-honeypot
ADMIN_URL_PREFIX = config('ADMIN_URL_PREFIX', default='_admin')
