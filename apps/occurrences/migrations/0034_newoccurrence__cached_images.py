# Generated by Django 3.1.9 on 2021-05-19 14:26

from django.db import migrations

import core.fields.json_field


class Migration(migrations.Migration):

    dependencies = [
        ('occurrences', '0033_auto_20210519_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='newoccurrence',
            name='_cached_images',
            field=core.fields.json_field.JSONField(default=list, editable=False),
        ),
    ]