# Generated by Django 3.1.13 on 2021-08-05 21:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collections', '0003_auto_20210610_1912'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='verified',
        ),
    ]
