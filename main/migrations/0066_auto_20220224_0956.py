# Generated by Django 3.2.12 on 2022-02-24 09:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0065_alter_cestdocument_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="approval",
            name="reason",
            field=models.OneToOneField(
                help_text="If you don't approve the case and need more information or want to approve with a conditional change add your note and select 'Reviewed'.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reason",
                to="main.comment",
                verbose_name="Additional information",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="text",
            field=models.TextField(
                help_text="You can provide additional information at any stage of the process, by adding a comment.",
                verbose_name="Add a comment",
            ),
        ),
    ]