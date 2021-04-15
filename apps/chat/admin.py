from apps.admin.model_admin import ModelAdmin, admin_site
from apps.chat import models


class ChatAdmin(ModelAdmin):
    """Model admin for searchable models."""

    model: models.Chat
    fields = ['content']


admin_site.register(models.Chat, ChatAdmin)
