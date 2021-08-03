from django.contrib import admin

from apps.moderation.admin import ModerationAdmin

from .models import Book


class BookAdmin(ModerationAdmin):
    pass


admin.site.register(Book, BookAdmin)
