# Generated by Django 3.1.9 on 2021-05-20 15:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0048_remove_quote__cached_images'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GenericQuoteRelation',
        ),
    ]
