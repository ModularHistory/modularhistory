# Generated by Django 3.0.7 on 2020-09-23 05:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0033_auto_20200923_0557'),
    ]

    operations = [
        migrations.CreateModel(
            name='Affidavit',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sources.documentsource',),
        ),
        migrations.AlterField(
            model_name='oldaffidavit',
            name='collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='oldaffidavit', to='sources.Collection'),
        ),
        migrations.AlterField(
            model_name='typedsource',
            name='type',
            field=models.CharField(choices=[('sources.textualsource', 'textual source'), ('sources.sourcewithpagenumbers', 'source with page numbers'), ('sources.piece', 'piece'), ('sources.essay', 'essay'), ('sources.documentsource', 'document source'), ('sources.document', 'document'), ('sources.affidavit', 'affidavit'), ('sources.article', 'article'), ('sources.book', 'book'), ('sources.chapter', 'chapter'), ('sources.correspondence', 'correspondence'), ('sources.email', 'email'), ('sources.letter', 'letter'), ('sources.memorandum', 'memorandum'), ('sources.spokensource', 'spoken source'), ('sources.speech', 'speech'), ('sources.address', 'address'), ('sources.discourse', 'discourse'), ('sources.lecture', 'lecture'), ('sources.sermon', 'sermon'), ('sources.statement', 'statement'), ('sources.interview', 'interview')], db_index=True, max_length=255),
        ),
    ]
