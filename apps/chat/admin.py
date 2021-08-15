from apps.admin.model_admin import ExtendedModelAdmin, admin_site
from apps.chat import models


class ChatAdmin(ExtendedModelAdmin):
    """Model admin for searchable models."""

    model: models.Chat
    fields = ['content']


admin_site.register(models.Chat, ChatAdmin)
