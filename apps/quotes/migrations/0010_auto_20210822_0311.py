# Generated by Django 3.1.13 on 2021-08-22 03:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0009_remove_quote_tags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quote',
            old_name='new_tags',
            new_name='tags',
        ),
    ]
