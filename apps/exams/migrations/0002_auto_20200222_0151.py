# Generated by Django 2.2.5 on 2020-02-21 20:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exams',
            name='students',
            field=models.ManyToManyField(related_name='exams_takenby_student', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='exams',
            name='classroom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams_in_classroom', to='classroom.Classroom'),
        ),
    ]