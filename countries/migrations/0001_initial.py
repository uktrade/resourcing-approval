# Generated by Django 3.2.11 on 2022-01-07 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "reference_id",
                    models.CharField(
                        max_length=11,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Reference ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                ("iso_1_code", models.CharField(max_length=3, unique=True)),
                ("iso_2_code", models.CharField(max_length=2, unique=True)),
                ("iso_3_code", models.CharField(max_length=3, unique=True)),
                ("overseas_region", models.CharField(max_length=40)),
                ("start_date", models.DateField(null=True)),
                ("end_date", models.DateField(null=True)),
            ],
        ),
    ]
