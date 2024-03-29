# Generated by Django 3.1.13 on 2021-08-19 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propositions', '0015_auto_20210816_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='argument',
            name='premises',
            field=models.ManyToManyField(
                help_text='The premises on which the argument depends.',
                related_name='supported_arguments',
                through='propositions.ArgumentSupport',
                to='propositions.Proposition',
                verbose_name='premises',
            ),
        ),
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
                help_text='The type of reasoning (see https://www.merriam-webster.com/words-at-play/deduction-vs-induction-vs-abduction).',
                null=True,
            ),
        ),
    ]
