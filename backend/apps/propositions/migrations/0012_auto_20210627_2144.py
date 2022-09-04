# Generated by Django 3.1.12 on 2021-06-27 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propositions', '0011_premisegroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='argument',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='argumentsupport',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='citation',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='fallacyidentification',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='imagerelation',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='location',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='premisegroup',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='quoterelation',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
    ]