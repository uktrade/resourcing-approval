# Generated by Django 3.2.11 on 2022-01-07 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("countries", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="overseas_region",
            field=models.CharField(max_length=40, null=True),
        ),
    ]
