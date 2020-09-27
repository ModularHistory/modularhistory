# Generated by Django 3.0.7 on 2020-09-17 14:45

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0016_auto_20200917_0824'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='typedsource',
            options={},
        ),
        migrations.AddField(
            model_name='typedsource',
            name='date_is_circa',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='typedsource',
            name='hidden',
            field=models.BooleanField(blank=True, default=False, help_text="Don't let this item appear in search results."),
        ),
        migrations.AddField(
            model_name='typedsource',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='typedsource',
            name='verified',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
