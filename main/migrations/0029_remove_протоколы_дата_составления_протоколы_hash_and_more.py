# Generated by Django 5.2.3 on 2025-07-04 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_alter_приказы_hash'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='протоколы',
            name='Дата_составления',
        ),
        migrations.AddField(
            model_name='протоколы',
            name='Hash',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='приказы',
            name='Hash',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
