# Generated by Django 3.2.9 on 2021-12-07 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0034_auto_20211206_1504"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="resourcingrequest",
            name="full_name",
        ),
    ]
