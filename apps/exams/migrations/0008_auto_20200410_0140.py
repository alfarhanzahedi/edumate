# Generated by Django 2.2.8 on 2020-04-10 01:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0007_auto_20200410_0111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='exam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='exams.Exam'),
        ),
    ]
