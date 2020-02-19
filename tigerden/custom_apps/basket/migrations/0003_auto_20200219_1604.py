# Generated by Django 2.2.10 on 2020-02-19 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('basket', '0002_auto_20200219_1604'),
        ('voucher', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='vouchers',
            field=models.ManyToManyField(blank=True, to='voucher.Voucher', verbose_name='Vouchers'),
        ),
        migrations.AlterUniqueTogether(
            name='line',
            unique_together={('basket', 'line_reference')},
        ),
    ]
