# Generated by Django 3.1.13 on 2021-08-25 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0016_auto_20210825_2338'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliation',
            name='deleted',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='affiliation',
            name='verified',
            field=models.BooleanField(default=False, verbose_name='verified'),
        ),
        migrations.AddField(
            model_name='role',
            name='deleted',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='verified',
            field=models.BooleanField(default=False, verbose_name='verified'),
        ),
        migrations.AddField(
            model_name='rolefulfillment',
            name='deleted',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='rolefulfillment',
            name='verified',
            field=models.BooleanField(default=False, verbose_name='verified'),
        ),
    ]
