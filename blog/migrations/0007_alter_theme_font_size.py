# Generated by Django 4.1.5 on 2023-03-06 09:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_theme_theme_name_delete_bookmark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='font_size',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(16), django.core.validators.MaxValueValidator(32)]),
        ),
    ]