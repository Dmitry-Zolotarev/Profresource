# Generated by Django 5.2.3 on 2025-07-06 12:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_remove_организации_адрес_remove_слушатели_адрес_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='почтовые_индексы',
            name='Населенный_пункт',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.населенные_пункты'),
        ),
        migrations.AlterField(
            model_name='улицы',
            name='Почтовый_индекс',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.почтовые_индексы'),
        ),
    ]
