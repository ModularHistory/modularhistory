# Generated by Django 3.0.10 on 2020-10-13 06:56

from django.db import migrations
import modularhistory.fields.json_field


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0012_quote_db_attributee_html'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quote',
            name='db_attributee_html',
        ),
        migrations.RemoveField(
            model_name='quote',
            name='db_citation_html',
        ),
        migrations.AddField(
            model_name='quote',
            name='computations',
            field=modularhistory.fields.json_field.JSONField(blank=True, default=dict, null=True),
        ),
    ]
