# Generated by Django 3.1.3 on 2020-11-27 23:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import core.fields.historic_datetime_field


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
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
                ('query', models.CharField(blank=True, max_length=100, null=True)),
                (
                    'ordering',
                    models.CharField(
                        choices=[('date', 'Date'), ('relevance', 'Relevance')],
                        max_length=10,
                    ),
                ),
                (
                    'start_year',
                    core.fields.historic_datetime_field.HistoricDateTimeField(
                        blank=True, null=True
                    ),
                ),
                (
                    'end_year',
                    core.fields.historic_datetime_field.HistoricDateTimeField(
                        blank=True, null=True
                    ),
                ),
            ],
            options={
                'verbose_name_plural': 'Searches',
            },
        ),
        migrations.CreateModel(
            name='UserSearch',
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
                ('datetime', models.DateTimeField(auto_now_add=True)),
                (
                    'search',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='user_searches',
                        to='search.search',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='searches',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
