from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from main.constants import ApproverGroup


class Command(BaseCommand):
    help = "Create the required groups"

    def handle(self, *args, **options):
        hiring_manager_group, _ = Group.objects.get_or_create(
            pk=1, name="Hiring Manager"
        )
        approver_group, _ = Group.objects.get_or_create(pk=2, name="Approver")
        hop_group, _ = Group.objects.get_or_create(
            pk=3, name=ApproverGroup.HEAD_OF_PROFESSION.value
        )
        chief_group, _ = Group.objects.get_or_create(
            pk=4, name=ApproverGroup.CHIEF.value
        )
        busops_group, _ = Group.objects.get_or_create(
            pk=5, name=ApproverGroup.BUSOPS.value
        )
        hrbp_group, _ = Group.objects.get_or_create(pk=6, name=ApproverGroup.HRBP.value)
        finance_group, _ = Group.objects.get_or_create(
            pk=7, name=ApproverGroup.FINANCE.value
        )
        commercial_group, _ = Group.objects.get_or_create(
            pk=8, name=ApproverGroup.COMMERCIAL.value
        )
        director_group, _ = Group.objects.get_or_create(
            pk=9, name=ApproverGroup.DIRECTOR.value
        )
        director_general_group, _ = Group.objects.get_or_create(
            pk=10, name=ApproverGroup.DIRECTOR_GENERAL.value
        )

        hiring_manager_group.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    # financialinformation
                    "add_financialinformation",
                    "view_financialinformation",
                    "change_financialinformation",
                    "delete_financialinformation",
                    # resourcingrequest
                    "add_resourcingrequest",
                    "view_resourcingrequest",
                    "change_resourcingrequest",
                    "delete_resourcingrequest",
                    # jobdescription
                    "add_jobdescription",
                    "view_jobdescription",
                    "change_jobdescription",
                    "delete_jobdescription",
                    # statementofwork
                    "add_statementofwork",
                    "view_statementofwork",
                    "change_statementofwork",
                    "delete_statementofwork",
                    # interimrequest
                    "add_interimrequest",
                    "view_interimrequest",
                    "change_interimrequest",
                    "delete_interimrequest",
                    # cestrationale
                    "add_cestrationale",
                    "view_cestrationale",
                    "change_cestrationale",
                    "delete_cestrationale",
                    # cestdocument
                    "add_cestdocument",
                    "view_cestdocument",
                    "change_cestdocument",
                    "delete_cestdocument",
                    # sdsstatusdetermination
                    "add_sdsstatusdetermination",
                    "view_sdsstatusdetermination",
                    "change_sdsstatusdetermination",
                    "delete_sdsstatusdetermination",
                    # comment
                    "add_comment",
                    "view_comment",
                    "change_comment",
                    "delete_comment",
                ],
                content_type__app_label="main",
            )
        )

        approver_group.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    "view_financialinformation",
                    "view_resourcingrequest",
                    "view_jobdescription",
                    "view_statementofwork",
                    "view_interimrequest",
                    "view_cestrationale",
                    "view_cestdocument",
                    "view_sdsstatusdetermination",
                    # comment
                    "add_comment",
                    "view_comment",
                    "change_comment",
                    "delete_comment",
                ],
                content_type__app_label="main",
            )
        )

        hop_group.permissions.set(
            [
                Permission.objects.get(
                    codename="can_give_head_of_profession_approval",
                    content_type__app_label="main",
                )
            ]
        )

        chief_group.permissions.set(
            [
                Permission.objects.get(
                    codename="can_give_chief_approval",
                    content_type__app_label="main",
                )
            ]
        )

        busops_group.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    "can_give_busops_approval",
                    "view_all_resourcingrequests",
                ],
                content_type__app_label="main",
            )
        )

        hrbp_group.permissions.set(
            [
                Permission.objects.get(
                    codename="can_give_hrbp_approval",
                    content_type__app_label="main",
                )
            ]
        )

        finance_group.permissions.set(
            [
                Permission.objects.get(
                    codename="can_give_finance_approval",
                    content_type__app_label="main",
                )
            ]
        )

        commercial_group.permissions.set(
            [
                Permission.objects.get(
                    codename="can_give_commercial_approval",
                    content_type__app_label="main",
                )
            ]
        )

        director_group.permissions.set(
            [
                Permission.objects.get(
                    codename="can_give_director_approval",
                    content_type__app_label="main",
                )
            ]
        )

        director_general_group.permissions.set(
            [
                Permission.objects.get(
                    codename="can_give_director_general_approval",
                    content_type__app_label="main",
                )
            ]
        )

        self.stdout.write(self.style.SUCCESS("Successfully created groups"))
