# Generated by Django 3.2.11 on 2022-01-21 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0056_delete_cestrationale"),
    ]

    operations = [
        migrations.AddField(
            model_name="financialinformation",
            name="team",
            field=models.CharField(default="Legacy Team", max_length=64),
            preserve_default=False,
        ),
    ]