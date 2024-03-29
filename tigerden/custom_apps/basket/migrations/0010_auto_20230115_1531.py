# Generated by Django 3.2.16 on 2023-01-15 21:31

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0009_line_date_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basket',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='line',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='lineattribute',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='lineattribute',
            name='value',
            field=models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder, verbose_name='Value'),
        ),
    ]
