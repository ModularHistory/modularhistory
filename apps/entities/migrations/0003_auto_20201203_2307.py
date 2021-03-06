# Generated by Django 3.1.4 on 2020-12-03 23:07

import django.db.models.deletion
from django.db import migrations, models

import modularhistory.fields.historic_datetime_field


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0002_auto_20201130_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorization',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categorizations', to='entities.category', verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='categorization',
            name='date',
            field=modularhistory.fields.historic_datetime_field.HistoricDateTimeField(blank=True, null=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='categorization',
            name='end_date',
            field=modularhistory.fields.historic_datetime_field.HistoricDateTimeField(blank=True, null=True, verbose_name='end date'),
        ),
        migrations.AlterField(
            model_name='categorization',
            name='entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorizations', to='entities.entity', verbose_name='entity'),
        ),
        migrations.AlterField(
            model_name='role',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='entities.entity', verbose_name='organization'),
        ),
        migrations.AlterField(
            model_name='rolefulfillment',
            name='affiliation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role_fulfillments', to='entities.affiliation', verbose_name='affiliation'),
        ),
        migrations.AlterField(
            model_name='rolefulfillment',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fulfillments', to='entities.role', verbose_name='role'),
        ),
    ]
