# Generated by Django 2.2.5 on 2020-03-08 18:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0010_auto_20200301_0259'),
    ]

    operations = [
        migrations.AddField(
            model_name='exams',
            name='active_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exams',
            name='active_time',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
