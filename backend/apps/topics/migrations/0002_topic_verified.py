# Generated by Django 3.1.13 on 2021-08-19 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='verified',
            field=models.BooleanField(default=False, verbose_name='verified'),
        ),
    ]
