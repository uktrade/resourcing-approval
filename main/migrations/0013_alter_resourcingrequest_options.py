# Generated by Django 3.2.9 on 2021-11-12 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0012_alter_resourcingrequest_state"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="resourcingrequest",
            options={
                "permissions": (
                    ("view_all_resourcingrequests", "Can view all resourcing requests"),
                )
            },
        ),
    ]