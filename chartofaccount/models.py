from django.db import models


class DepartmentalGroup(models.Model):
    group_code = models.CharField("Group Code", primary_key=True, max_length=6)
    group_name = models.CharField("Group Name", max_length=300)

    @property
    def full_name(self):
        return "{self.group_code} - {self.group_name}"

    def __str__(self):
        return str(self.group_name)

    class Meta:
        ordering = ["group_name"]


class Directorate(models.Model):
    directorate_code = models.CharField(
        "Directorate Code", primary_key=True, max_length=6
    )
    directorate_name = models.CharField("Directorate Name", max_length=300)
    group = models.ForeignKey(
        DepartmentalGroup, on_delete=models.CASCADE, related_name="directorates"
    )

    def __str__(self):
        return str(self.directorate_name)

    class Meta:
        ordering = ["directorate_name"]


class CostCentre(models.Model):
    cost_centre_code = models.CharField(
        "Cost Centre Code", primary_key=True, max_length=6
    )
    cost_centre_name = models.CharField("Cost Centre Name", max_length=300)
    directorate = models.ForeignKey(
        Directorate, on_delete=models.CASCADE, related_name="cost_centres"
    )

    @property
    def full_name(self):
        return f"{self.cost_centre_code} - {self.cost_centre_name}"

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["cost_centre_code"]


class ProgrammeCode(models.Model):
    programme_code = models.CharField(
        "Programme Code",
        primary_key=True,
        max_length=50,
    )
    programme_description = models.CharField(
        "Programme Name",
        max_length=100,
    )

    def __str__(self):
        return self.programme_code + " - " + self.programme_description

    class Meta:
        verbose_name_plural = "Programme Codes"
        ordering = ["programme_code"]


class ProjectCode(models.Model):
    project_code = models.CharField(
        "Project Code",
        primary_key=True,
        max_length=50,
    )
    project_description = models.CharField(
        max_length=300, verbose_name="Project Description"
    )

    def __str__(self):
        return self.project_code + " - " + self.project_description

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["project_code"]
