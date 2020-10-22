from entities import models
from entities.forms import IdeaForm
from admin.model_admin import admin_site, ModelAdmin


class IdeaAdmin(ModelAdmin):
    """Admin for ideas."""

    model = models.Idea
    add_form = IdeaForm


admin_site.register(models.Idea, IdeaAdmin)
