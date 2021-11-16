# Generated by Django 3.2.9 on 2021-11-16 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0015_rename_name_resourcingrequest_full_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="approval",
            name="type",
            field=models.CharField(
                choices=[
                    ("head_of_profession", "Head of Profession"),
                    ("chief", "Chief"),
                    ("busops", "BusOps"),
                    ("hrbp", "HRBP"),
                    ("finance", "Finance"),
                    ("commercial", "Commercial"),
                ],
                max_length=20,
            ),
        ),
    ]
