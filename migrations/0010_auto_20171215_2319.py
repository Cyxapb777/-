# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-15 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labApp', '0009_auto_20171214_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computer',
            name='type',
            field=models.CharField(choices=[('Personal Computer', 'Personal computer'), ('Laptop', 'Laptop'), ('Monoblock', 'Monoblock')], default='Personal Computer', max_length=30),
        ),
    ]
