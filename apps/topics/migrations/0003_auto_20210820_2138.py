# Generated by Django 3.1.13 on 2021-08-20 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0002_topic_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='deleted',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='title',
            field=models.CharField(
                blank=True,
                help_text='This value can be used as a page header and/or title attribute.',
                max_length=120,
                verbose_name='title',
            ),
        ),
    ]