# Generated by Django 3.2.11 on 2022-02-02 15:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("change_log", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="change",
            old_name="diff",
            new_name="changes",
        ),
        migrations.RemoveField(
            model_name="change",
            name="object_repr",
        ),
    ]