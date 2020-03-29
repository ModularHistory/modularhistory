import uuid

from django.db.models import (
    Model as BaseModel,
    BooleanField,
    UUIDField
)


class SearchableMixin(BaseModel):
    verified = BooleanField(default=False, blank=True)
    hidden = BooleanField(
        default=False, blank=True,
        help_text="Don't let this item appear in search results."
    )
    key = UUIDField(primary_key=False, default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True
