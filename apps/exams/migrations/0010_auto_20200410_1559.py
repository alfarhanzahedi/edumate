# Generated by Django 2.2.8 on 2020-04-10 15:59

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0009_auto_20200410_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='body',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True),
        ),
    ]
