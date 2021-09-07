# Generated by Django 3.1.13 on 2021-08-21 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0008_auto_20210820_2138'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='imagerelation',
            managers=[],
        ),
        migrations.AlterModelManagers(
            name='quoterelation',
            managers=[],
        ),
        migrations.RemoveField(
            model_name='quoterelation',
            name='deleted',
        ),
        migrations.AddField(
            model_name='imagerelation',
            name='verified',
            field=models.BooleanField(default=False, verbose_name='verified'),
        ),
    ]
