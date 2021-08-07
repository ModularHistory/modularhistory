# Generated by Django 3.1.13 on 2021-08-07 19:31

import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.moderation.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
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
                    'reasons',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.PositiveSmallIntegerField(
                            choices=[
                                (0, 'Elaboration or expansion'),
                                (1, 'Correction of content'),
                                (2, 'Correction of grammar or punctuation'),
                            ]
                        ),
                        blank=True,
                        help_text='Reason(s) for change(s)',
                        null=True,
                        size=None,
                    ),
                ),
                (
                    'description',
                    models.TextField(
                        blank=True, help_text='Description of changes made', null=True
                    ),
                ),
                (
                    'draft_state',
                    models.PositiveSmallIntegerField(
                        choices=[(0, 'Draft'), (1, 'Ready for moderation')],
                        default=0,
                        editable=False,
                    ),
                ),
                (
                    'moderation_status',
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, 'Rejected'),
                            (1, 'Pending'),
                            (2, 'Approved'),
                            (3, 'Merged'),
                        ],
                        default=1,
                        editable=False,
                    ),
                ),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                (
                    'object_id',
                    models.PositiveIntegerField(
                        blank=True, db_index=True, editable=False, null=True
                    ),
                ),
                (
                    'changed_object',
                    apps.moderation.fields.SerializedObjectField(editable=False),
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
        migrations.CreateModel(
            name='Moderation',
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
                    'verdict',
                    models.PositiveSmallIntegerField(
                        choices=[(0, 'Rejected'), (1, 'Pending'), (2, 'Approved')]
                    ),
                ),
                ('reason', models.TextField(blank=True, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                (
                    'change',
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='moderations',
                        to='moderation.change',
                    ),
                ),
                (
                    'moderator',
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='moderations',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ContentContribution',
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
                    'change',
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='contributions',
                        to='moderation.change',
                    ),
                ),
                (
                    'contributor',
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='content_contributions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ChangeSet',
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
                    'reasons',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.PositiveSmallIntegerField(
                            choices=[
                                (0, 'Elaboration or expansion'),
                                (1, 'Correction of content'),
                                (2, 'Correction of grammar or punctuation'),
                            ]
                        ),
                        blank=True,
                        help_text='Reason(s) for change(s)',
                        null=True,
                        size=None,
                    ),
                ),
                (
                    'description',
                    models.TextField(
                        blank=True, help_text='Description of changes made', null=True
                    ),
                ),
                (
                    'draft_state',
                    models.PositiveSmallIntegerField(
                        choices=[(0, 'Draft'), (1, 'Ready for moderation')],
                        default=0,
                        editable=False,
                    ),
                ),
                (
                    'moderation_status',
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, 'Rejected'),
                            (1, 'Pending'),
                            (2, 'Approved'),
                            (3, 'Merged'),
                        ],
                        default=1,
                        editable=False,
                    ),
                ),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                (
                    'initiator',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='initiated_changesets',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'modification',
                'verbose_name_plural': 'modifications',
                'ordering': ['moderation_status', 'created_date'],
            },
        ),
        migrations.AddField(
            model_name='change',
            name='contributors',
            field=models.ManyToManyField(
                through='moderation.ContentContribution', to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='change',
            name='set',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='moderation.changeset',
            ),
        ),
        migrations.CreateModel(
            name='Approval',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('moderation.moderation',),
        ),
        migrations.CreateModel(
            name='Rejection',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('moderation.moderation',),
        ),
    ]
