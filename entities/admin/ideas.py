from admin import admin_site, Admin
from .. import models
from ..forms import (
    IdeaForm
)


class IdeaAdmin(Admin):
    model = models.Idea
    add_form = IdeaForm


admin_site.register(models.Idea, IdeaAdmin)
