# Generated by Django 3.1.13 on 2021-07-30 00:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0002_auto_20210727_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='creator',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cms_issue_set',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='pullrequest',
            name='creator',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cms_pullrequest_set',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name='Commit',
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
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('url', models.URLField(verbose_name='URL')),
                ('sha', models.CharField(max_length=100)),
                ('message', models.TextField()),
                (
                    'committer',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='commits',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'creator',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='cms_commit_set',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'parents',
                    models.ManyToManyField(
                        blank=True, related_name='children', to='cms.Commit'
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Branch',
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
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('url', models.URLField(verbose_name='URL')),
                (
                    'commit',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to='cms.commit',
                    ),
                ),
                (
                    'creator',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='cms_branch_set',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'source',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='branches',
                        to='cms.branch',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='commits',
            field=models.ManyToManyField(related_name='pull_requests', to='cms.Commit'),
        ),
    ]
