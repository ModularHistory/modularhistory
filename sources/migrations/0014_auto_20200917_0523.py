# Generated by Django 3.0.7 on 2020-09-17 05:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0012_auto_20200909_0442'),
        ('places', '0002_auto_20200909_0442'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('sources', '0013_auto_20200917_0520'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Piece',
            new_name='OldPiece',
        ),
    ]
