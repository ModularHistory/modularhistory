# Generated by Django 3.1.13 on 2021-08-21 05:30

from typing import TYPE_CHECKING, Type

import django.db.models.deletion
from django.db import migrations, models

import apps.topics.models.taggable
import core.fields.m2m_foreign_key

if TYPE_CHECKING:
    from apps.sources.models.source import Source as _Source
    from apps.topics.models.topic import Topic


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Source: Type['_Source'] = apps.get_model('sources', 'Source')
    TopicRelation = apps.get_model('sources', 'TopicRelation')
    s: '_Source'
    for s in Source.objects.all():
        tag: 'Topic'
        for tag in s.tags.all():
            TopicRelation.objects.get_or_create(topic=tag, content_object=s)


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0003_auto_20210820_2138'),
        ('sources', '0008_auto_20210821_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='tags',
            field=models.ManyToManyField(
                blank=True,
                related_name='sources_source_set',
                to='topics.Topic',
                verbose_name='tags',
            ),
        ),
        migrations.CreateModel(
            name='TopicRelation',
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
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('verified', models.BooleanField(default=False, verbose_name='verified')),
                ('position', models.PositiveSmallIntegerField(blank=True, default=0)),
                (
                    'content_object',
                    core.fields.m2m_foreign_key.ManyToManyForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='topic_relations',
                        to='sources.source',
                        verbose_name='source',
                    ),
                ),
                (
                    'topic',
                    core.fields.m2m_foreign_key.ManyToManyForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sources_topicrelation_set',
                        to='topics.topic',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='source',
            name='new_tags',
            field=apps.topics.models.taggable.TagsField(
                blank=True,
                related_name='source_set',
                through='sources.TopicRelation',
                to='topics.Topic',
                verbose_name='tags',
            ),
        ),
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]
