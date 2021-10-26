# Generated by Django 3.2.8 on 2021-10-25 16:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatementOfWorkModule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("module_title", models.CharField(max_length=255)),
                ("completion_date", models.DateField()),
            ],
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="cost_centre_code",
            field=models.CharField(max_length=6),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="deliverable_notes",
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="end_date",
            field=models.DateField(),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="exceptional_expenses",
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="fees",
            field=models.TextField(verbose_name="Project fee and invoicing"),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="hiring_manager_team_leader",
            field=models.CharField(
                max_length=255, verbose_name="Hiring manager / Team lead (if different)"
            ),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="is_nominated_worker",
            field=models.BooleanField(
                choices=[(True, "Yes"), (False, "No")],
                null=True,
                verbose_name="Did DDaT find them or not?",
            ),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="notice_period",
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="programme_code",
            field=models.CharField(max_length=4),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="project_code",
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="project_description",
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="role",
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="slot_code",
            field=models.CharField(max_length=30),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="start_date",
            field=models.DateField(),
        ),
        migrations.AddField(
            model_name="statementofwork",
            name="team_directorate",
            field=models.CharField(max_length=255, verbose_name="Team/Directorate"),
        ),
        migrations.CreateModel(
            name="StatementOfWorkModuleDeliverable",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("deliverable_title", models.CharField(max_length=255)),
                ("deliverable_description", models.TextField()),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("monthly_fee", models.DecimalField(decimal_places=2, max_digits=9)),
                ("payment_date", models.DateField()),
                (
                    "statement_of_work_module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deliverables",
                        to="main.statementofworkmodule",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="statementofworkmodule",
            name="statement_of_work",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modules",
                to="main.statementofwork",
            ),
        ),
    ]