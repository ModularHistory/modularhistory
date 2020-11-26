# Generated by Django 3.1.3 on 2020-11-25 19:54

import django.db.models.deletion
from django.db import migrations, models

import modularhistory.fields
import modularhistory.fields.html_field


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0004_remove_entity_parent_organization'),
        ('occurrences', '0008_auto_20201118_2018'),
        ('topics', '0005_auto_20201118_2005'),
        ('facts', '0005_auto_20201121_1757'),
    ]

    operations = [
        migrations.RenameModel('Fact', 'Postulation'),
        migrations.RenameModel('FactSupport', 'PostulationSupport'),
        migrations.AlterField(
            model_name='postulation',
            name='supportive_facts',
            field=models.ManyToManyField(related_name='supported_facts', through='facts.PostulationSupport', to='facts.Postulation'),
        ),
        migrations.AlterField(
            model_name='entityfactrelation',
            name='fact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fact_entity_relations', to='facts.postulation'),
        ),
        migrations.AlterField(
            model_name='occurrencefactrelation',
            name='fact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fact_occurrence_relations', to='facts.postulation'),
        ),
        migrations.AlterField(
            model_name='topicfactrelation',
            name='fact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fact_topic_relations', to='facts.postulation'),
        )
    ]
