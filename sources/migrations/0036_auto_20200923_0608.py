# Generated by Django 3.0.7 on 2020-09-23 06:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0002_auto_20200909_0442'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('entities', '0012_auto_20200909_0442'),
        ('sources', '0035_auto_20200923_0605'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='JournalEntry',
            new_name='OldJournalEntry',
        ),
    ]
