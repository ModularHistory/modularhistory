# Generated by Django 3.1.13 on 2021-08-26 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0006_auto_20210826_0221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='height',
            field=models.PositiveSmallIntegerField(blank=True, verbose_name='height'),
        ),
        migrations.AlterField(
            model_name='image',
            name='width',
            field=models.PositiveSmallIntegerField(blank=True, verbose_name='width'),
        ),
    ]
