# Generated by Django 2.2.8 on 2020-04-09 09:14

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0005_examsubmission_is_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='solution',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True),
        ),
    ]
