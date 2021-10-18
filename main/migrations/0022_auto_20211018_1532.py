# Generated by Django 3.2.8 on 2021-10-18 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0021_auto_20211018_1328"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="contractorapproval",
            name="check_status",
        ),
        migrations.AddConstraint(
            model_name="contractorapproval",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("chief_approval__isnull", True),
                        ("commercial_approval__isnull", True),
                        ("finance_approval__isnull", True),
                        ("hrbp_approval__isnull", True),
                        ("status", 0),
                    ),
                    ("status", 1),
                    models.Q(("chief_approval", True), ("status", 2)),
                    models.Q(
                        ("chief_approval", True),
                        ("commercial_approval", True),
                        ("finance_approval", True),
                        ("hrbp_approval", True),
                        ("status", 3),
                    ),
                    _connector="OR",
                ),
                name="check_status",
            ),
        ),
    ]
