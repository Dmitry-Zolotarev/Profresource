# Generated by Django 5.2.3 on 2025-06-29 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='слушатели',
            name='Номер_паспорта',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
