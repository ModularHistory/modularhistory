# Generated by Django 3.1.11 on 2021-05-27 19:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('propositions', '0013_auto_20210525_0341'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='support',
            options={'verbose_name': 'support'},
        ),
        migrations.AlterUniqueTogether(
            name='support',
            unique_together={('premise', 'conclusion')},
        ),
    ]