# Generated by Django 2.2.dev20180521165340 on 2018-06-07 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='course_dept',
            field=models.CharField(blank=True, default='', max_length=7),
        ),
        migrations.AlterField(
            model_name='item',
            name='course_number',
            field=models.IntegerField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='item',
            name='prof_last_name',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
