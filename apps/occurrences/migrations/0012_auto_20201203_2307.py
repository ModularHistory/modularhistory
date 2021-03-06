# Generated by Django 3.1.4 on 2020-12-03 23:07

from django.db import migrations

import modularhistory.fields
import modularhistory.fields.html_field


class Migration(migrations.Migration):

    dependencies = [
        ('occurrences', '0011_auto_20201203_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='occurrence',
            name='description',
            field=modularhistory.fields.HTMLField(paragraphed=True, processor=modularhistory.fields.html_field.process, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='summary',
            field=modularhistory.fields.HTMLField(paragraphed=False, processor=modularhistory.fields.html_field.process, verbose_name='summary'),
        ),
    ]
