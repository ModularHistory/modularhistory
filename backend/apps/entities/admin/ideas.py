from apps.admin.model_admin import ExtendedModelAdmin, admin_site
from apps.entities import models
from apps.entities.forms import IdeaForm


class IdeaAdmin(ExtendedModelAdmin):
    """Admin for ideas."""

    model = models.Idea
    add_form = IdeaForm


admin_site.register(models.Idea, IdeaAdmin)
