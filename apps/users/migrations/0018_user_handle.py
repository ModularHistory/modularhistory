# Generated by Django 3.1.13 on 2021-08-25 22:11

import autoslug.fields
from django.db import migrations

import apps.users.models
from apps.users.models import User


def forwards_func(apps, schema_editor):
    for user in User.objects.all():
        user.save()  # this will set the user's handle


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20210727_0301'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='handle',
            field=autoslug.fields.AutoSlugField(
                editable=False,
                null=True,
                populate_from=apps.users.models.get_handle_base,
                slugify=apps.users.models.handlify,
                unique=True,
                verbose_name='handle',
            ),
        ),
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]
