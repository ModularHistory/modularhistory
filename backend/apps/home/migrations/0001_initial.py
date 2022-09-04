# Generated by Django 3.2.8 on 2021-10-27 19:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'object_id',
                    models.PositiveIntegerField(
                        blank=True, db_index=True, editable=False, null=True
                    ),
                ),
                (
                    'start_date',
                    models.DateTimeField(blank=True, null=True, verbose_name='start date'),
                ),
                (
                    'end_date',
                    models.DateTimeField(blank=True, null=True, verbose_name='end date'),
                ),
                (
                    'content_type',
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='contenttypes.contenttype',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]