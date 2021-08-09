from apps.moderation.models.moderation import Moderation
from core.celery import app


@app.task
def handle_moderation(moderation_id: int):
    """Post-process a moderation."""
    moderation: Moderation = Moderation.objects.get(pk=moderation_id)
    change = moderation.change
    print(f'Debugging: {moderation=}; {change=}')
