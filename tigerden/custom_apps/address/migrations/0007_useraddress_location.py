# Generated by Django 2.2.9 on 2020-02-02 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0006_auto_20181115_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='location',
            field=models.CharField(default='Tiger Den', max_length=120, verbose_name='Location'),
        ),
    ]