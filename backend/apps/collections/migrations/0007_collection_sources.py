# Generated by Django 3.2.7 on 2021-10-22 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0017_collectioninclusion'),
        ('collections', '0006_collection_quotes'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='sources',
            field=models.ManyToManyField(
                blank=True,
                related_name='collections',
                through='sources.CollectionInclusion',
                to='sources.Source',
            ),
        ),
    ]
