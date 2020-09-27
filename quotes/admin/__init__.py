"""
Admin modules and/or classes for the quotes app.

This __init__.py must import modules containing admin_site registrations,
as well as any modules/classes to be made accessible elsewhere.
"""

from . import quote_admin
from .related_quotes_inline import RelatedQuotesInline  # accessible to other apps
