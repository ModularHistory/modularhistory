# Generated by Django 3.2.9 on 2021-12-03 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0008_auto_20211021_0144'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='alt_text',
            field=models.CharField(blank=True, max_length=255, verbose_name='alt text'),
        ),
    ]
