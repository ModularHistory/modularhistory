# Generated by Django 3.1.13 on 2021-08-23 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0014_remove_source_related_entities'),
    ]

    operations = [
        migrations.RenameField(
            model_name='source',
            old_name='new_related_entities',
            new_name='related_entities',
        ),
    ]
