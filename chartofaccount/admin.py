from django.contrib import admin

# Register your models here.
from chartofaccount.models import (
    Directorate,
    DepartmentalGroup,
    CostCentre,
    ProjectCode,
    ProgrammeCode,
)


admin.site.register(Directorate)
admin.site.register(DepartmentalGroup)
admin.site.register(CostCentre)
admin.site.register(ProjectCode)
admin.site.register(ProgrammeCode)
