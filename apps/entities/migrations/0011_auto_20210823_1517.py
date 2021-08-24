# Generated by Django 3.1.13 on 2021-08-23 15:17

import django.db.models.deletion
from django.db import migrations, models

import apps.entities.models.model_with_related_entities
import core.fields.m2m_foreign_key


def forwards_func(apps, schema_editor):
    Entity = apps.get_model('entities', 'Entity')
    EntityRelation = apps.get_model('entities', 'EntityRelation')
    for entity in Entity.objects.all():
        for related_entity in entity.related_entities.all():
            EntityRelation.objects.get_or_create(entity=related_entity, content_object=entity)


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0010_auto_20210821_0530'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntityRelation',
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
                (
                    'content_object',
                    core.fields.m2m_foreign_key.ManyToManyForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='entity_relations',
                        to='entities.entity',
                        verbose_name='entity',
                    ),
                ),
                (
                    'entity',
                    core.fields.m2m_foreign_key.ManyToManyForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='entities_entityrelation_set',
                        to='entities.entity',
                        verbose_name='related entity',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='entity',
            name='new_related_entities',
            field=apps.entities.models.model_with_related_entities.RelatedEntitiesField(
                blank=True,
                related_name='entity_nre',
                through='entities.EntityRelation',
                to='entities.Entity',
                verbose_name='related entities',
            ),
        ),
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]