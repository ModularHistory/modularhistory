# Generated by Django 3.2.9 on 2021-11-04 20:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20210825_2212'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAddress',
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
                    'email',
                    models.EmailField(
                        max_length=254, unique=True, verbose_name='e-mail address'
                    ),
                ),
                ('verified', models.BooleanField(default=False, verbose_name='verified')),
                ('primary', models.BooleanField(default=False, verbose_name='primary')),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='user',
                    ),
                ),
            ],
            options={
                'verbose_name': 'email address',
                'verbose_name_plural': 'email addresses',
            },
        ),
    ]
