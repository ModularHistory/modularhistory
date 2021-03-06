# Generated by Django 3.1.4 on 2020-12-06 20:36

import gm2m.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sources', '0010_auto_20201206_0224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='related',
            field=gm2m.fields.GM2MField('quotes.Quote', 'occurrences.Occurrence', blank=True, related_name='sources', through='sources.Citation', through_fields=['source', 'content_object', 'content_type', 'object_id']),
        ),
    ]
