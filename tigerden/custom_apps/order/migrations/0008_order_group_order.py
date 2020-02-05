# Generated by Django 2.2.9 on 2020-02-02 22:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grouporder', '__first__'),
        ('order', '0007_auto_20181115_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='group_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='grouporder.GroupOrder', verbose_name='Group Order'),
        ),
    ]