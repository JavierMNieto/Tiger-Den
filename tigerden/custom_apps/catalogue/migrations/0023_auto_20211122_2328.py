# Generated by Django 3.1.13 on 2021-11-23 05:28

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import oscar.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0022_auto_20210210_0539'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='option',
            options={'ordering': ['code'], 'verbose_name': 'Product option', 'verbose_name_plural': 'Product options'},
        ),
        migrations.AddField(
            model_name='option',
            name='option_group',
            field=models.ForeignKey(blank=True, help_text='Select an option group if using type "Option" or "Multi Option"', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_options', to='catalogue.attributeoptiongroup', verbose_name='Option Group'),
        ),
        migrations.AddField(
            model_name='product',
            name='is_supervisor_only',
            field=models.BooleanField(default=False, help_text='Only show product availability to supervisors', verbose_name='Is for supervisors only?'),
        ),
        migrations.AddField(
            model_name='product',
            name='limited_day',
            field=models.IntegerField(choices=[(-1, 'Every Day'), (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')], default=-1, help_text='Only show this product on a specific day.', verbose_name="Time of product's availability"),
        ),
        migrations.AlterField(
            model_name='option',
            name='code',
            field=models.SlugField(max_length=128, validators=[django.core.validators.RegexValidator(message="Code can only contain the letters a-z, A-Z, digits, and underscores, and can't start with a digit.", regex='^[a-zA-Z_][0-9a-zA-Z_]*$'), oscar.core.validators.non_python_keyword], verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='option',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='option',
            name='required',
            field=models.BooleanField(default=False, verbose_name='Required'),
        ),
        migrations.AlterField(
            model_name='option',
            name='type',
            field=models.CharField(choices=[('text', 'Text'), ('integer', 'Integer'), ('boolean', 'True / False'), ('float', 'Float'), ('richtext', 'Rich Text'), ('date', 'Date'), ('datetime', 'Datetime'), ('option', 'Option'), ('multi_option', 'Multi Option'), ('entity', 'Entity'), ('file', 'File'), ('image', 'Image')], default='text', max_length=20, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='productclass',
            name='requires_shipping',
            field=models.BooleanField(default=False, verbose_name='Requires shipping?'),
        ),
    ]
