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
    group = models.ForeignKey(DepartmentalGroup, on_delete=models.CASCADE, related_name="directorates")

    def __str__(self):
        return str(self.directorate_name)

    class Meta:
        ordering = ["directorate_name"]


class CostCentre(models.Model):
    cost_centre_code = models.CharField(
        "Cost Centre Code", primary_key=True, max_length=6
    )
    cost_centre_name = models.CharField("Cost Centre Name", max_length=300)
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE, related_name="cost_centres")

    @property
    def full_name(self):
        return f"{self.cost_centre_code} - {self.cost_centre_name}"

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["cost_centre_code"]



