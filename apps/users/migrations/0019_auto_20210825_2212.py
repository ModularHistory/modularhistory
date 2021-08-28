# Generated by Django 3.1.13 on 2021-08-25 22:12

import autoslug.fields
from django.db import migrations

import apps.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_user_handle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='handle',
            field=autoslug.fields.AutoSlugField(
                editable=False,
                populate_from=apps.users.models.get_handle_base,
                slugify=apps.users.models.handlify,
                unique=True,
                verbose_name='handle',
            ),
        ),
    ]