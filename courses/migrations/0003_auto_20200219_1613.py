# Generated by Django 2.2 on 2020-02-19 16:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20200215_1336'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['position', 'name']},
        ),
        migrations.AlterModelOptions(
            name='coursetype',
            options={'ordering': ['name', 'level']},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['name']},
        ),
    ]