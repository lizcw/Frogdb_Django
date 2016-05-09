# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-09 01:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frogs', '0008_auto_20160509_1118'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteconfiguration',
            name='report_contactdetails',
        ),
        migrations.RemoveField(
            model_name='siteconfiguration',
            name='report_generalnotes',
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='report_contact_details',
            field=models.CharField(default='Contact Details', max_length=2000),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='report_general_notes',
            field=models.CharField(default='General Notes', max_length=5000),
        ),
    ]
