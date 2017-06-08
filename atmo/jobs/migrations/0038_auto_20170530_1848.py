# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 18:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0037_populate_temp_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparkjobrunalert',
            name='run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='jobs.SparkJobRun'),
        ),
        migrations.AlterField(
            model_name='sparkjobrunalert',
            name='temp_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]