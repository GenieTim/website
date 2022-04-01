# Generated by Django 3.2.12 on 2022-03-23 13:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0013_eventcategorytranslation_teaser'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='date_to',
            field=models.DateField(blank=True, help_text='If start and end are on different days', null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='registration_enabled',
            field=models.BooleanField(default=False,
                                      help_text='Gives participants of the event the possibility to register'),
        ),
        migrations.AlterField(
            model_name='eventtranslation',
            name='name',
            field=models.CharField(max_length=255, verbose_name="[TR] The name of this event (e.g. 'Open Dancing')"),
        ),
        migrations.AlterField(
            model_name='eventtranslation',
            name='price_special',
            field=models.CharField(blank=True, max_length=255, null=True,
                                   verbose_name='[TR] Set this only if you want a different price schema.'),
        ),
    ]