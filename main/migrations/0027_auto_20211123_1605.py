# Generated by Django 3.2.9 on 2021-11-23 16:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0026_auto_20211123_1600"),
    ]

    operations = [
        migrations.AddField(
            model_name="resourcingrequest",
            name="director_approval",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="director_approval",
                to="main.approval",
            ),
        ),
        migrations.AddField(
            model_name="resourcingrequest",
            name="director_general_approval",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="director_general_approval",
                to="main.approval",
            ),
        ),
    ]
