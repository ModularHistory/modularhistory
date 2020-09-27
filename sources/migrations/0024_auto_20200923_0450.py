# Generated by Django 3.0.7 on 2020-09-23 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0023_auto_20200923_0100'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpokenSource',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sources.typedsource',),
        ),
        migrations.AddField(
            model_name='typedsource',
            name='type2',
            field=models.CharField(choices=[('address', 'address'), ('discourse', 'discourse'), ('lecture', 'lecture'), ('sermon', 'sermon'), ('speech', 'speech'), ('statement', 'statement')], default='speech', max_length=10),
        ),
        migrations.AlterField(
            model_name='typedsource',
            name='type',
            field=models.CharField(choices=[('sources.textualsource', 'textual source'), ('sources.sourcewithpagenumbers', 'source with page numbers'), ('sources.article', 'article'), ('sources.book', 'book'), ('sources.chapter', 'chapter'), ('sources.spokensource', 'spoken source'), ('sources.speech', 'speech'), ('sources.address', 'address'), ('sources.discourse', 'discourse'), ('sources.lecture', 'lecture'), ('sources.sermon', 'sermon'), ('sources.statement', 'statement')], db_index=True, max_length=255),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Addresses',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sources.spokensource',),
        ),
        migrations.CreateModel(
            name='Discourse',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Discourses',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sources.spokensource',),
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Lectures',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sources.spokensource',),
        ),
        migrations.CreateModel(
            name='Sermon',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Sermons',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sources.spokensource',),
        ),
        migrations.CreateModel(
            name='Speech',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Speeches',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sources.spokensource',),
        ),
        migrations.CreateModel(
            name='Statement',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Statements',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sources.spokensource',),
        ),
    ]
