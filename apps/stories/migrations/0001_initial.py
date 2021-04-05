# Generated by Django 3.1.7 on 2021-04-05 20:26

import django.db.models.deletion
from django.db import migrations, models

import modularhistory.fields
import modularhistory.fields.html_field


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Story',
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
                    'notes',
                    modularhistory.fields.HTMLField(
                        blank=True,
                        null=True,
                        paragraphed=True,
                        processor=modularhistory.fields.html_field.process,
                    ),
                ),
                ('handle', models.CharField(max_length=40, unique=True)),
                (
                    'description',
                    modularhistory.fields.HTMLField(
                        blank=True,
                        null=True,
                        paragraphed=True,
                        processor=modularhistory.fields.html_field.process,
                        verbose_name='description',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StoryElement',
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
                ('key', models.CharField(max_length=40, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StoryInspiration',
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
                    'downstream_story',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='inspirations_in',
                        to='stories.story',
                    ),
                ),
                (
                    'upstream_story',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='inspirations_out',
                        to='stories.story',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StoryElementInclusion',
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
                    'justification',
                    modularhistory.fields.HTMLField(
                        blank=True,
                        null=True,
                        paragraphed=True,
                        processor=modularhistory.fields.html_field.process,
                    ),
                ),
                (
                    'story',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='stories.story'
                    ),
                ),
                (
                    'story_element',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='stories.storyelement',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='story',
            name='elements',
            field=models.ManyToManyField(
                related_name='stories',
                through='stories.StoryElementInclusion',
                to='stories.StoryElement',
                verbose_name='story elements',
            ),
        ),
        migrations.AddField(
            model_name='story',
            name='upstream_stories',
            field=models.ManyToManyField(
                related_name='downstream_stories',
                through='stories.StoryInspiration',
                to='stories.Story',
                verbose_name='upstream stories',
            ),
        ),
    ]
