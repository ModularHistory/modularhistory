# Generated by Django 3.1.11 on 2021-05-28 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0004_convert_nulls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='name',
            field=models.CharField(
                blank=True, default='', max_length=40, unique=True, verbose_name='name'
            ),
            preserve_default=False,
        ),
    ]