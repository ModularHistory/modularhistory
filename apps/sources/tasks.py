from apps.sources.models import Source
from core.celery import app


@app.task
def update_source(pk: int):
    source: Source = Source.objects.get(pk=pk)
    source.update_calculated_fields()
    source.save()
