# Generated by Django 3.1.13 on 2021-09-06 01:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('flatpages', '0003_auto_20210902_0823'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='flatpage',
            options={
                'ordering': ['path'],
                'verbose_name': 'flat page',
                'verbose_name_plural': 'flat pages',
            },
        ),
        migrations.RenameField(model_name='flatpage', old_name='url', new_name='path'),
        migrations.AlterUniqueTogether(
            name='flatpage',
            unique_together={('path',)},
        ),
    ]
