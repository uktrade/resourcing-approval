from chartofaccount.models import Directorate, CostCentre
from main.models import Approval


def get_user_related_approval_types(user):
    for approval_type in Approval.Type:
        if user.has_perm(f"main.can_give_{approval_type.value}_approval"):
            yield approval_type


def syncronise_cost_centre_dropdowns(
    form,
    group_field="group",
    directorate_field="directorate",
    cost_centre_field="cost_centre_code",
):

    # The three dropdowns group/directorate/cost_centre are linked.
    # The group selection  is used to filter the directorate list.
    # The directorate selection  is used to filter the cost_centre list.

    clear_directorate = True
    clear_cost_centre = True

    if group_field in form.data:
        # if a group has been selected, we can populate the other lists.
        if directorate_field in form.data:
            # if we have a directorate, populate the cost centres
            try:
                directorate_code = form.data.get(directorate_field)
                form.fields[cost_centre_field].queryset = CostCentre.objects.filter(
                    directorate=directorate_code
                ).order_by("cost_centre_name")
                clear_cost_centre = False
            except (ValueError, TypeError):
                pass

            try:
                # Populate the directorate
                group_code = form.data.get(group_field)
                form.fields[directorate_field].queryset = Directorate.objects.filter(
                    group=group_code
                ).order_by("directorate_name")
                clear_directorate = False
            except (ValueError, TypeError):
                pass

    elif form.instance.pk:
        # Update case: set the cost_centre and directorate dropdown
        # using the instance values
        try:
            form.fields[
                cost_centre_field
            ].queryset = form.instance.directorate.cost_centres.order_by(
                "cost_centre_name"
            )
            clear_cost_centre = False
        except (ValueError, TypeError):
            pass

        try:
            form.fields[
                directorate_field
            ].queryset = form.instance.group.directorates.order_by("directorate_name")
            clear_directorate = False
        except (ValueError, TypeError):
            pass

    if clear_directorate:
        form.fields[directorate_field].queryset = Directorate.objects.none()
        # if there are no directorates, clear the cost centre too.
        clear_cost_centre = True

    if clear_cost_centre:
        form.fields[cost_centre_field].queryset = CostCentre.objects.none()
