# Generated by Django 2.2.9 on 2020-02-22 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0002_auto_20200219_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productclass',
            name='track_stock',
            field=models.BooleanField(default=True, verbose_name='Track stock levels?'),
        ),
    ]