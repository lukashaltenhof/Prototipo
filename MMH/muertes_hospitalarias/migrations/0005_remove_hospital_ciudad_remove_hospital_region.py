# Generated by Django 5.1.2 on 2024-10-20 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muertes_hospitalarias', '0004_hospital_ciudad'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hospital',
            name='ciudad',
        ),
        migrations.RemoveField(
            model_name='hospital',
            name='region',
        ),
    ]
