# Generated by Django 3.2.11 on 2022-01-07 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("countries", "0002_alter_country_overseas_region"),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="iso_1_code",
            field=models.CharField(
                max_length=3, unique=True, verbose_name="ISO 1 Code"
            ),
        ),
        migrations.AlterField(
            model_name="country",
            name="iso_2_code",
            field=models.CharField(
                max_length=2, unique=True, verbose_name="ISO 2 Code"
            ),
        ),
        migrations.AlterField(
            model_name="country",
            name="iso_3_code",
            field=models.CharField(
                max_length=3, unique=True, verbose_name="ISO 3 Code"
            ),
        ),
    ]
