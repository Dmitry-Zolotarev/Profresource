# Generated by Django 5.2.3 on 2025-07-07 04:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_remove_населенные_пункты_тип_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='улицы',
            name='Почтовый_индекс',
        ),
        migrations.AddField(
            model_name='адреса',
            name='Почтовый_индекс',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.почтовые_индексы'),
        ),
        migrations.AddField(
            model_name='улицы',
            name='Населенный_пункт',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.населенные_пункты'),
        ),
    ]
