# Generated by Django 5.2.3 on 2025-06-29 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_слушатели_номер_паспорта'),
    ]

    operations = [
        migrations.AlterField(
            model_name='типы_курсов',
            name='Название',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
