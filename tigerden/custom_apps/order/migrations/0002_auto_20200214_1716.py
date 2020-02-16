# Generated by Django 2.2.10 on 2020-02-14 23:16

from django.db import migrations, models
import oscar.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouporder',
            name='currency',
            field=models.CharField(default=oscar.core.utils.get_default_currency, max_length=14, verbose_name='Currency'),
        ),
    ]