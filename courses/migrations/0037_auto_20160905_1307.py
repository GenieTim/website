# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-05 11:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0036_auto_20160902_1135'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentCourse',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('courses.course',),
        ),
        migrations.CreateModel(
            name='PlannedCourse',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('courses.course',),
        ),
        migrations.RemoveField(
            model_name='roomtranslation',
            name='teacher_info',
        ),
        migrations.AddField(
            model_name='roomtranslation',
            name='instructions',
            field=models.TextField(blank=True, help_text='Instructions to prepare the room (for teachers/staff only)', null=True),
        ),
        migrations.AlterField(
            model_name='musicpluginmodel',
            name='cmsplugin_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='courses_musicpluginmodel', serialize=False, to='cms.CMSPlugin'),
        ),
    ]
