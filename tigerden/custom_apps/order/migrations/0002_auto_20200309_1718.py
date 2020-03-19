# Generated by Django 2.2.11 on 2020-03-09 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='max_alloc_credit',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=12, null=True, verbose_name='Maximum Amount of Credit Allowed to Use'),
        ),
    ]
