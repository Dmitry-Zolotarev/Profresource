# Generated by Django 5.2.3 on 2025-07-06 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_alter_месяцы_название'),
    ]

    operations = [
        migrations.AlterField(
            model_name='типы_населенных_пунктов',
            name='Название',
            field=models.CharField(max_length=100),
        ),
    ]
