# Generated by Django 3.1.13 on 2021-07-24 00:27

import django_cryptography.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_socialaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialaccount',
            name='access_token',
            field=django_cryptography.fields.encrypt(
                models.CharField(default='1', max_length=200)
            ),
            preserve_default=False,
        ),
    ]
