# Generated by Django 2.2.8 on 2020-04-11 18:21

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='post_html',
        ),
        migrations.RemoveField(
            model_name='post',
            name='post_raw',
        ),
        migrations.AddField(
            model_name='post',
            name='post',
            field=ckeditor_uploader.fields.RichTextUploadingField(default=''),
            preserve_default=False,
        ),
    ]