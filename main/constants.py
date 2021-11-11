from enum import Enum, unique

from main.models import Approval


@unique
class ApproverGroup(Enum):
    HEAD_OF_PROFESSION = "Head of Profession"
    CHIEF = "Chief"
    BUSOPS = "BusOps"
    HRBP = "HRBP"
    FINANCE = "Finance"
    COMMERCIAL = "Commercial"


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
}
