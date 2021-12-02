from typing import TYPE_CHECKING, Optional

from django.urls import path

from apps.admin.model_admin import ExtendedModelAdmin, admin_site
from apps.collections.views import CollectionSearchView
from apps.entities.views import EntityCategorySearchView, EntitySearchView
from apps.moderation.admin.moderated_model import ModeratedModelAdmin
from apps.search import models
from apps.topics.views import TagSearchView
from apps.users.views import UserSearchView

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.urls.resolvers import URLPattern

    from apps.search.models import SearchableModel


class SearchableModelAdmin(ModeratedModelAdmin):
    """Model admin for searchable models."""

    model: type['SearchableModel']

    exclude = ['cache', 'tags']
    readonly_fields = []

    def get_fields(
        self, request: 'HttpRequest', model_instance: Optional['SearchableModel'] = None
    ) -> list[str]:
        """Return reordered fields to be displayed in the admin."""
        fields = list(super().get_fields(request, model_instance))
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

    def get_fieldsets(
        self, request: 'HttpRequest', model_instance: Optional['SearchableModel'] = None
    ) -> list[tuple]:
        """Return the fieldsets to be displayed in the admin form."""
        fields, fieldsets = list(self.get_fields(request, model_instance)), []
        meta_fields = [
            fields.pop(fields.index(field))
            for field in (
                'notes',
                'verified',
            )
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
                    'More',
                    {
                        'classes': ('collapse',),
                        'fields': collapsed_fields,
                    },
                )
            )
        return fieldsets

    def get_urls(self) -> list['URLPattern']:
        """Return URLs used by searchable model admins."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'tag_search/',
                self.admin_site.admin_view(TagSearchView.as_view(model_admin=self)),
                name='tag_search',
            ),
            path(
                'user_search/',
                self.admin_site.admin_view(UserSearchView.as_view(model_admin=self)),
                name='user_search',
            ),
            path(
                'collection_search/',
                self.admin_site.admin_view(CollectionSearchView.as_view(model_admin=self)),
                name='collection_search',
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


class SearchAdmin(ExtendedModelAdmin):
    """Admin for user searches."""

    list_display = ['pk']


admin_site.register(models.Search, SearchAdmin)
