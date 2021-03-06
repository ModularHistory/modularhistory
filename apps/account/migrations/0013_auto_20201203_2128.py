# Generated by Django 3.1.4 on 2020-12-03 21:28

import functools

from django.db import migrations, models

import modularhistory.fields.file_field


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_auto_20201016_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=functools.partial(modularhistory.fields.file_field._generate_upload_path, *(), **{'path': 'account/avatars'}), verbose_name='avatar'),
        ),
    ]
