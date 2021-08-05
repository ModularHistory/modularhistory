from django.contrib import admin

from apps.moderation.admin import ChangeSetAdmin

from .models import Book


class BookAdmin(ChangeSetAdmin):
    pass


admin.site.register(Book, BookAdmin)
