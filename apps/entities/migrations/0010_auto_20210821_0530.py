# Generated by Django 3.1.13 on 2021-08-21 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0009_auto_20210821_0002'),
    ]

    operations = [
        migrations.AddField(
            model_name='quoterelation',
            name='deleted',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='quoterelation',
            name='verified',
            field=models.BooleanField(default=False, verbose_name='verified'),
        ),
    ]
