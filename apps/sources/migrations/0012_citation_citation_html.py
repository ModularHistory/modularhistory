# Generated by Django 3.1.9 on 2021-05-17 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0011_auto_20210517_0131'),
    ]

    operations = [
        migrations.AddField(
            model_name='citation',
            name='citation_html',
            field=models.TextField(blank=True, null=True),
        ),
    ]
