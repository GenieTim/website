# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-15 11:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import filer.fields.image


class Migration(migrations.Migration):

    replaces = [('cms_plugins', '0001_initial'), ('cms_plugins', '0002_thumbnailpluginmodel'), ('cms_plugins', '0003_auto_20160905_1307'), ('cms_plugins', '0004_auto_20170203_1940'), ('cms_plugins', '0005_countdownpluginmodel'), ('cms_plugins', '0006_countdownpluginmodel_text'), ('cms_plugins', '0007_countdownpluginmodel_finish_text'), ('cms_plugins', '0008_upcomingeventsandcoursespluginmodel')]

    initial = True

    dependencies = [
        ('cms', '0001_initial'),
        ('cms', '0016_auto_20160608_1535'),
        ('filer', '0001_initial'),
        ('djangocms_link', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ButtonPluginModel',
            fields=[
                ('link_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='djangocms_link.Link')),
                ('emphasize', models.BooleanField(default=False, help_text='If this button should be visually emphasized.')),
            ],
            options={
                'abstract': False,
            },
            bases=('djangocms_link.link',),
        ),
        migrations.CreateModel(
            name='PageTitlePluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='cms_plugins_pagetitlepluginmodel', serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(blank=True, help_text="The title to be displayed. Leave empty to display the page's title.", max_length=30, null=True)),
                ('subtitle', models.CharField(blank=True, help_text='The subtitle to be displayed.', max_length=50, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='ThumbnailPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='cms_plugins_thumbnailpluginmodel', serialize=False, to='cms.CMSPlugin')),
                ('image', filer.fields.image.FilerImageField(blank=True, help_text='Image to show thumbnail for.', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.FILER_IMAGE_MODEL)),
                ('crop', models.BooleanField(default=False, help_text='If this thumbnail should be cropped to fit given size.')),
                ('url', models.URLField(blank=True, help_text='URL to display on image click.', max_length=500, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='CountdownPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='cms_plugins_countdownpluginmodel', serialize=False, to='cms.CMSPlugin')),
                ('finish_datetime', models.DateTimeField(help_text='Countdown finish date and time.')),
                ('hide', models.BooleanField(default=True, help_text='Hide Countdown after finished.')),
                ('text', models.TextField(blank=True, max_length=255, null=True)),
                ('finish_text', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='UpcomingEventsAndCoursesPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='cms_plugins_upcomingeventsandcoursespluginmodel', serialize=False, to='cms.CMSPlugin')),
                ('delta_days', models.IntegerField(blank=True, help_text='Events and courses within the time delta (in days) from now on are shown.Leave empty to make no restrictions.', null=True)),
                ('max_displayed', models.IntegerField(blank=True, help_text='Maximum number of items to be displayed. Leave empty to make no restrictions.', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]