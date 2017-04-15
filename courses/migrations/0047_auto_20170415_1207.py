# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-15 12:07
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0046_bankaccount_bank_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_city',
            field=models.CharField(blank=True, help_text='City of the bank.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_country',
            field=django_countries.fields.CountryField(blank=True, default='CH', max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_name',
            field=models.CharField(blank=True, help_text='Name of the bank.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='bank_zip_code',
            field=models.CharField(blank=True, help_text='Zipcode of the bank.', max_length=255, null=True),
        ),
    ]