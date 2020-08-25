from django.db import models
from django.contrib.flatpages.models import FlatPage


class StaticPage(FlatPage):
    meta_description = models.TextField(max_length=200)
