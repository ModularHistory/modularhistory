from entities import models
from entities.forms import (
    IdeaForm
)
from history.admin import admin_site, Admin


class IdeaAdmin(Admin):
    """TODO: add docstring."""

    model = models.Idea
    add_form = IdeaForm


admin_site.register(models.Idea, IdeaAdmin)
