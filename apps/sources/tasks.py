from apps.sources.models.source import Source
from core.celery import app


@app.task
def update_source(pk: int):
    """Asynchronously update a source's calculated fields."""
    source: Source = Source.objects.get(pk=pk)
    source.update_calculated_fields()
    source.save()
