# Generated by Django 3.1.9 on 2021-05-18 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0017_auto_20210518_1624'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='cached_tags',
            new_name='_cached_tags',
        ),
        migrations.RenameField(
            model_name='video',
            old_name='cached_tags',
            new_name='_cached_tags',
        ),
    ]