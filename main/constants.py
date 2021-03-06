from enum import Enum, unique

from main.models import Approval


@unique
class ApproverGroup(Enum):
    HEAD_OF_PROFESSION = "Head of Profession"
    CHIEF = "Chief"
    BUSOPS = "Workforce Planning"
    HRBP = "HR Business Partners"
    FINANCE = "Finance"
    COMMERCIAL = "Commercial"
    DIRECTOR = "Director"
    DG_COO = "DG COO"


GROUP_APPROVER_PK = 2

GROUP_USER_ADMIN = "User Administrator"
GROUP_SYSTEM_ADMIN = "System Administrator"


assert set(x.value for x in ApproverGroup) == set(
    x.label for x in Approval.Type
), "ApproverGroup and Approval.Type are out of sync"


APPROVAL_TYPE_TO_GROUP = {
    Approval.Type.HEAD_OF_PROFESSION: ApproverGroup.HEAD_OF_PROFESSION,
    Approval.Type.CHIEF: ApproverGroup.CHIEF,
    Approval.Type.BUSOPS: ApproverGroup.BUSOPS,
    Approval.Type.HRBP: ApproverGroup.HRBP,
    Approval.Type.FINANCE: ApproverGroup.FINANCE,
    Approval.Type.COMMERCIAL: ApproverGroup.COMMERCIAL,
    Approval.Type.DIRECTOR: ApproverGroup.DIRECTOR,
    Approval.Type.DG_COO: ApproverGroup.DG_COO,
}
