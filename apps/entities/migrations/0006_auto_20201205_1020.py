# Generated by Django 3.1.4 on 2020-12-05 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0005_auto_20201203_2316'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entityidea',
            options={'verbose_name': 'entity idea'},
        ),
        migrations.AlterModelOptions(
            name='idea',
            options={'verbose_name': 'idea'},
        ),
    ]
