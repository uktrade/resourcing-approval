from django.contrib import admin

from chartofaccount.models import (
    CostCentre,
    DepartmentalGroup,
    Directorate,
    ProgrammeCode,
    ProjectCode,
)


admin.site.register(Directorate)
admin.site.register(DepartmentalGroup)
admin.site.register(CostCentre)
admin.site.register(ProjectCode)
admin.site.register(ProgrammeCode)
