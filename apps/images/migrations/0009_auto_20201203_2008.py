# Generated by Django 3.1.4 on 2020-12-03 20:08

from django.db import migrations

import modularhistory.fields.json_field


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0008_image_cropping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='links',
            field=modularhistory.fields.json_field.JSONField(blank=True, default=dict),
        ),
    ]
