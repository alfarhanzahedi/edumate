# Generated by Django 2.2.5 on 2020-03-21 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0018_auto_20200321_1324'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exams',
            old_name='duration_datetime',
            new_name='end_datetime',
        ),
    ]