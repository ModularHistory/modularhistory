from admin.model_admin import ModelAdmin, admin_site
from entities import models
from entities.forms import IdeaForm


class IdeaAdmin(ModelAdmin):
    """Admin for ideas."""

    model = models.Idea
    add_form = IdeaForm


admin_site.register(models.Idea, IdeaAdmin)
