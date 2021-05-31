from typing import TYPE_CHECKING, Type

from django.urls import path

from apps.admin.model_admin import ModelAdmin, admin_site
from apps.entities.views import EntityCategorySearchView, EntitySearchView
from apps.search import models
from apps.topics.views import TagSearchView

if TYPE_CHECKING:
    from apps.search.models import SearchableModel


class SearchableModelAdmin(ModelAdmin):
    """Model admin for searchable models."""

    model: Type['SearchableModel']

    exclude = ['cache', 'tags']
    readonly_fields = ['slug', 'pretty_cache']

    def get_fields(self, request, model_instance=None):
        """Return reordered fields to be displayed in the admin."""
        fields = super().get_fields(request, model_instance)
        ordered_field_names = reversed(
            [
                'notes',
                'type',
                'title',
                'slug',
                'summary',
                'certainty',
                'elaboration',
            ]
        )
        for field_name in ordered_field_names:
            if field_name in fields:
                fields.remove(field_name)
                fields.insert(0, field_name)
        return fields

    def get_fieldsets(self, request, model_instance=None):
        """Return the fieldsets to be displayed in the admin form."""
        fields, fieldsets = list(self.get_fields(request, model_instance)), []
        meta_fields = [
            fields.pop(fields.index(field))
            for field in ('notes', 'verified', 'hidden')
            if field in fields
        ]
        if meta_fields:
            fieldsets.append(('Meta', {'fields': meta_fields}))
        essential_fields = [
            fields.pop(fields.index(field))
            for field in ('type', 'title', 'slug')
            if field in fields
        ]
        if essential_fields:
            fieldsets.append((None, {'fields': essential_fields}))
        date_fields = [
            fields.pop(fields.index(field))
            for field in ('date_is_circa', 'date', 'end_date')
            if field in fields
        ]
        if date_fields:
            fieldsets.append(
                ('Date', {'fields': date_fields}),
            )
        collapsed_fields = [
            fields.pop(fields.index(field))
            for field in ('pretty_cache', 'cache')
            if field in fields
        ]
        fieldsets.append((None, {'fields': fields}))
        if collapsed_fields and model_instance:
            fieldsets.append(
                (
                    None,
                    {
                        'classes': ('collapse',),
                        'fields': collapsed_fields,
                    },
                )
            )
        return fieldsets

    def get_urls(self):
        """Return URLs used by searchable model admins."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'tag_search/',
                self.admin_site.admin_view(TagSearchView.as_view(model_admin=self)),
                name='tag_search',
            ),
            path(
                'entity_search/',
                self.admin_site.admin_view(EntitySearchView.as_view(model_admin=self)),
                name='entity_search',
            ),
            path(
                'entity_category_search/',
                self.admin_site.admin_view(
                    EntityCategorySearchView.as_view(model_admin=self)
                ),
                name='entity_category_search',
            ),
        ]
        return custom_urls + urls


class SearchAdmin(ModelAdmin):
    """Admin for user searches."""

    list_display = ['pk']


admin_site.register(models.Search, SearchAdmin)
