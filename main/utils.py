from chartofaccount.models import Directorate
from main.models import Approval


def get_user_related_approval_types(user, resourcing_request=None):
    for approval_type in Approval.Type:
        # BusOps can clear all approvals.
        if (
            resourcing_request
            and resourcing_request.can_clear_approval
            and user.has_perm("main.can_give_busops_approval")
        ):
            yield approval_type
        elif user.has_perm(f"main.can_give_{approval_type.value}_approval"):
            yield approval_type


def syncronise_cost_centre_dropdowns(
    form,
    group_field="group",
    directorate_field="directorate",
):

    # The two dropdowns group/directorate are linked.
    # The group selection  is used to filter the directorate list.

    clear_directorate = True

    if group_field in form.data:
        # if a group has been selected, we can populate the other lists.
        if directorate_field in form.data:
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
        # Update case: set the directorate dropdown using the instance values
        try:
            form.fields[
                directorate_field
            ].queryset = form.instance.group.directorates.order_by("directorate_name")
            clear_directorate = False
        except (ValueError, TypeError):
            pass

    if clear_directorate:
        form.fields[directorate_field].queryset = Directorate.objects.none()
