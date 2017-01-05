# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-05 17:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0038_auto_20160906_1116'),
        ('payment', '0005_auto_20160704_1158'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoursePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_payments', to='courses.Course')),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_payments', to='payment.Payment')),
            ],
        ),
    ]