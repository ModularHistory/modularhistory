# Generated by Django 3.1.13 on 2021-08-16 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propositions', '0014_auto_20210628_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='argument',
            name='type',
            field=models.PositiveSmallIntegerField(
                choices=[
                    (None, '-------'),
                    (1, 'deductive'),
                    (2, 'inductive'),
                    (3, 'abductive'),
                ],
                db_index=True,
                null=True,
            ),
        ),
    ]
