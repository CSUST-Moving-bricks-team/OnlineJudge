# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-24 03:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conf', '0002_auto_20171011_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='judgeserver',
            name='is_disabled',
            field=models.BooleanField(default=False),
        ),
    ]