# Generated by Django 3.1.13 on 2021-08-24 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0007_remove_topic_related_topics'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='new_related_topics',
        ),
        migrations.AddField(
            model_name='topic',
            name='related_topics',
            field=models.ManyToManyField(
                blank=True,
                related_name='_topic_related_topics_+',
                through='topics.TopicRelation',
                to='topics.Topic',
            ),
        ),
    ]
