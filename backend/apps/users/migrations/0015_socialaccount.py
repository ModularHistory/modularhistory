# Generated by Django 3.1.13 on 2021-07-23 23:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_remove_user_locked'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialAccount',
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
                    'provider',
                    models.CharField(
                        choices=[
                            ('discord', 'Discord'),
                            ('facebook', 'Facebook'),
                            ('github', 'GitHub'),
                            ('google', 'Google'),
                            ('twitter', 'Twitter'),
                        ],
                        max_length=10,
                    ),
                ),
                ('uid', models.CharField(max_length=200)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'unique_together': {('provider', 'uid'), ('user', 'provider')},
            },
        ),
    ]
