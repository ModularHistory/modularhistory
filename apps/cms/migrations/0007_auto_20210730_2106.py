# Generated by Django 3.1.13 on 2021-07-30 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0006_auto_20210730_1939'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='branch',
            name='title',
        ),
        migrations.RemoveField(
            model_name='commit',
            name='title',
        ),
        migrations.AddField(
            model_name='branch',
            name='name',
            field=models.CharField(
                default='main', max_length=100, unique=True, verbose_name='name'
            ),
            preserve_default=False,
        ),
    ]
