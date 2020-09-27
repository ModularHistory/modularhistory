# Generated by Django 3.0.7 on 2020-09-21 13:31

from django.db import migrations, models
import django.db.models.deletion
import history.fields.historic_datetime_field


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0021_auto_20200921_1313'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sources.textualsource',),
        ),
        migrations.RenameField(
            model_name='oldbook',
            old_name='original_book',
            new_name='original_edition',
        ),
        migrations.AddField(
            model_name='typedsource',
            name='original_edition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subsequent_editions', to='sources.TypedSource'),
        ),
        migrations.AddField(
            model_name='typedsource',
            name='original_publication_date',
            field=history.fields.historic_datetime_field.HistoricDateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='typedsource',
            name='type',
            field=models.CharField(choices=[('sources.textualsource', 'textual source'), ('sources.sourcewithpagenumbers', 'source with page numbers'), ('sources.article', 'article'), ('sources.book', 'book'), ('sources.chapter', 'chapter')], db_index=True, max_length=255),
        ),
    ]
